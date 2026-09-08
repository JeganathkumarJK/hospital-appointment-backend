from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Appointment, AuditLog, Notification, Waitlist, User
from schemas import AppointmentCreate, AppointmentReschedule, AppointmentResponse
from ml_model import ai_engine
import datetime
import threading
import json
import urllib.request
import os

router = APIRouter(prefix="/appointments", tags=["Appointments"])

SNS_WEBHOOK_URL = os.getenv(
    "SNS_WEBHOOK_URL",
    "https://api.agents.snsihub.ai/webhook/3ce767f5-a4dc-46c7-8b6b-66a2c7adab87"
)

def trigger_sns_reminder_webhook(payload: dict):
    """Dispatches real-time booking and reminder event to SNS Agent Workbench."""
    def _send():
        try:
            req = urllib.request.Request(
                SNS_WEBHOOK_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                print(f"[SNS Workbench Notification] Webhook triggered successfully (HTTP {resp.status})")
        except Exception as e:
            print(f"[SNS Webhook Info] Notification event sent: {e}")
    threading.Thread(target=_send, daemon=True).start()

def serialize_apt(apt: Appointment) -> dict:
    return {
        "id": apt.id,
        "patientId": apt.patient_id,
        "patient": apt.patient,
        "doctor": apt.doctor,
        "department": apt.department,
        "date": apt.date,
        "time": apt.time,
        "type": apt.type,
        "probability": apt.probability,
        "risk": apt.risk,
        "status": apt.status,
        "notes": apt.notes or "",
    }

@router.get("", response_model=List[dict])
def get_all_appointments(
    date: Optional[str] = None,
    doctor: Optional[str] = None,
    status: Optional[str] = None,
    risk: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Appointment)
    if date:
        query = query.filter(Appointment.date == date)
    if doctor:
        query = query.filter(Appointment.doctor.ilike(f"%{doctor}%"))
    if status and status != "ALL":
        query = query.filter(Appointment.status == status)
    if risk and risk != "ALL":
        query = query.filter(Appointment.risk == risk)

    results = query.order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    return [serialize_apt(a) for a in results]

@router.get("/{apt_id}", response_model=dict)
def get_single_appointment(apt_id: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return serialize_apt(apt)

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    # Calculate sequential ID: A001, A002...
    total = db.query(Appointment).count()
    apt_id = f"A{str(total + 1).zfill(3)}"

    # Run AI prediction for no-show risk
    # Calculate days lead time
    lead_time = 3
    if data.date:
        try:
            target_dt = datetime.datetime.strptime(data.date, "%Y-%m-%d").date()
            today = datetime.date.today()
            lead_time = max(0, (target_dt - today).days)
        except Exception:
            lead_time = 3

    prediction = ai_engine.predict(
        lead_time_days=lead_time,
        department=data.department,
        appointment_date=data.date,
        sms_sent=True
    )

    new_apt = Appointment(
        id=apt_id,
        patient_id=data.patientId or "P001",
        patient=data.patient,
        doctor=data.doctor,
        department=data.department,
        date=data.date,
        time=data.time,
        type=data.type or "Consultation",
        probability=int(prediction["no_show_probability"] * 100),
        risk=prediction["risk_level"],
        status="CONFIRMED",
        notes=data.notes or ""
    )
    db.add(new_apt)

    # Log action
    log = AuditLog(
        action="CREATE_APPOINTMENT",
        performed_by="Patient Portal / Front Desk",
        details=f"Appointment {apt_id} booked for {data.patient} with {data.doctor}."
    )
    db.add(log)
    db.commit()
    db.refresh(new_apt)

    # Automatically notify SNS Agent Workbench
    patient_user = db.query(User).filter(User.id == new_apt.patient_id).first()
    email = patient_user.email if patient_user else "jeganathkumar2003@gmail.com"
    phone = patient_user.phone if patient_user else "+91 98765 43210"

    trigger_sns_reminder_webhook({
        "appointmentId": new_apt.id,
        "patientId": new_apt.patient_id,
        "patientName": new_apt.patient,
        "patientEmail": email,
        "patientPhone": phone,
        "doctor": new_apt.doctor,
        "department": new_apt.department,
        "date": new_apt.date,
        "time": new_apt.time,
        "type": new_apt.type,
        "riskLevel": new_apt.risk,
        "noShowProbability": new_apt.probability
    })

    return serialize_apt(new_apt)

@router.post("/{apt_id}/confirm", response_model=dict)
def confirm_appointment(apt_id: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    apt.status = "CONFIRMED"
    # Re-evaluate AI risk with confirmed status (reduces risk probability)
    apt.probability = max(5, int(apt.probability * 0.6))
    if apt.probability < 30:
        apt.risk = "LOW"
    elif apt.probability < 60:
        apt.risk = "MEDIUM"

    db.commit()
    db.refresh(apt)
    return serialize_apt(apt)

@router.post("/{apt_id}/cancel", response_model=dict)
def cancel_appointment(apt_id: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    apt.status = "CANCELLED"
    db.commit()
    db.refresh(apt)
    return serialize_apt(apt)

@router.post("/{apt_id}/reschedule", response_model=dict)
def reschedule_appointment(apt_id: str, data: AppointmentReschedule, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    apt.date = data.date
    apt.time = data.time
    apt.status = "CONFIRMED"

    # Re-calculate AI prediction for new slot
    prediction = ai_engine.predict(
        department=apt.department,
        appointment_date=data.date,
        sms_sent=True
    )
    apt.probability = int(prediction["no_show_probability"] * 100)
    apt.risk = prediction["risk_level"]

    db.commit()
    db.refresh(apt)
    return serialize_apt(apt)

@router.post("/{apt_id}/check-in", response_model=dict)
def check_in_appointment(apt_id: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    apt.status = "CHECKED_IN"
    apt.probability = 0
    apt.risk = "LOW"
    db.commit()
    db.refresh(apt)
    return serialize_apt(apt)

@router.post("/{apt_id}/complete", response_model=dict)
def complete_appointment(apt_id: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    apt.status = "COMPLETED"
    db.commit()
    db.refresh(apt)
    return serialize_apt(apt)

@router.post("/{apt_id}/no-show", response_model=dict)
def mark_appointment_no_show(apt_id: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    apt.status = "NO_SHOW"
    db.commit()
    db.refresh(apt)
    return serialize_apt(apt)

@router.delete("/{apt_id}")
def delete_appointment(apt_id: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail=f"Appointment {apt_id} not found")

    deleted_patient = apt.patient
    deleted_date = f"{apt.date} at {apt.time}"
    db.delete(apt)
    db.commit()

    return {
        "status": "success",
        "message": f"Appointment {apt_id} for {deleted_patient} ({deleted_date}) deleted successfully.",
        "deletedId": apt_id
    }
