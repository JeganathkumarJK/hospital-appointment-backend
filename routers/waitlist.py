from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Waitlist, AuditLog
from schemas import WaitlistCreate

router = APIRouter(prefix="/waitlist", tags=["Smart Waitlist"])

def serialize_waitlist(w: Waitlist) -> dict:
    return {
        "id": w.id,
        "patientId": w.patient_id,
        "patient": w.patient,
        "doctor": w.doctor,
        "department": w.department,
        "date": w.date,
        "time": w.time,
        "priority": w.priority,
        "status": w.status,
    }

@router.get("", response_model=List[dict])
def get_waitlist(db: Session = Depends(get_db)):
    items = db.query(Waitlist).order_by(Waitlist.created_at.desc()).all()
    return [serialize_waitlist(w) for w in items]

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_to_waitlist(data: WaitlistCreate, db: Session = Depends(get_db)):
    total = db.query(Waitlist).count()
    w_id = f"W{str(total + 1).zfill(3)}"

    entry = Waitlist(
        id=w_id,
        patient_id=data.patientId,
        patient=data.patient,
        doctor=data.doctor,
        department=data.department,
        date=data.date,
        time=data.time,
        priority=data.priority or "MEDIUM",
        status="WAITING"
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return serialize_waitlist(entry)

@router.post("/{waitlist_id}/offer-slot", response_model=dict)
def offer_slot(waitlist_id: str, db: Session = Depends(get_db)):
    item = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Waitlist record not found")

    item.status = "SLOT_OFFERED"
    db.commit()
    db.refresh(item)
    return serialize_waitlist(item)

@router.post("/{waitlist_id}/accept", response_model=dict)
def accept_slot(waitlist_id: str, db: Session = Depends(get_db)):
    item = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Waitlist record not found")

    item.status = "ACCEPTED"
    db.commit()
    db.refresh(item)
    return serialize_waitlist(item)

@router.post("/{waitlist_id}/decline", response_model=dict)
def decline_slot(waitlist_id: str, db: Session = Depends(get_db)):
    item = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Waitlist record not found")

    item.status = "DECLINED"
    db.commit()
    db.refresh(item)
    return serialize_waitlist(item)

@router.delete("/{waitlist_id}")
def delete_waitlist_item(waitlist_id: str, db: Session = Depends(get_db)):
    item = db.query(Waitlist).filter(Waitlist.id == waitlist_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Waitlist record {waitlist_id} not found")

    deleted_patient = item.patient
    db.delete(item)
    db.commit()

    return {
        "status": "success",
        "message": f"Waitlist record {waitlist_id} for {deleted_patient} deleted successfully.",
        "deletedId": waitlist_id
    }
