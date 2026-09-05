from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Doctor
from schemas import DoctorCreate, DoctorResponse

router = APIRouter(tags=["Doctors & Departments"])

def serialize_doctor(d: Doctor) -> dict:
    return {
        "id": d.id,
        "name": d.name,
        "department": d.department,
        "specialization": d.specialization or "General Practice",
        "room": d.room or "Clinic Room",
        "hours": d.hours or "09:00 AM – 04:00 PM",
        "appointments": d.appointments,
        "completed": d.completed,
        "cancelled": d.cancelled,
        "highRisk": d.high_risk,
        "utilization": d.utilization,
    }

@router.get("/doctors", response_model=List[dict])
def get_all_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    return [serialize_doctor(d) for d in doctors]

@router.post("/doctors", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_doctor(data: DoctorCreate, db: Session = Depends(get_db)):
    total = db.query(Doctor).count()
    doc_id = f"D{str(total + 1).zfill(3)}"

    clean_name = data.name.strip()
    formatted_name = clean_name if clean_name.lower().startswith("dr.") else f"Dr. {clean_name}"

    doctor = Doctor(
        id=doc_id,
        name=formatted_name,
        department=data.department,
        specialization=data.specialization or "Specialist",
        room=data.room or "Room 101",
        hours=data.hours or "09:00 AM – 04:00 PM",
        appointments=0,
        completed=0,
        cancelled=0,
        high_risk=0,
        utilization=50
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return serialize_doctor(doctor)

@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    # Distinct departments from doctors table
    depts = db.query(Doctor.department).distinct().all()
    return [{"name": d[0]} for d in depts]
