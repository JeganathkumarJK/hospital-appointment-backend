from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Appointment, Doctor, Notification, AuditLog

router = APIRouter(tags=["Analytics, Notifications & Audit"])

@router.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    total = db.query(Appointment).count()
    confirmed = db.query(Appointment).filter(Appointment.status == "CONFIRMED").count()
    pending = db.query(Appointment).filter(Appointment.status == "PENDING").count()
    completed = db.query(Appointment).filter(Appointment.status == "COMPLETED").count()
    high_risk = db.query(Appointment).filter(Appointment.risk == "HIGH").count()

    all_apts = db.query(Appointment).all()
    avg_risk = round(sum(a.probability for a in all_apts) / max(1, len(all_apts)), 1)

    doctors = db.query(Doctor).all()
    avg_utilization = round(sum(d.utilization for d in doctors) / max(1, len(doctors)), 1)

    return {
        "totalAppointments": total,
        "confirmedCount": confirmed,
        "pendingCount": pending,
        "completedCount": completed,
        "highRiskCount": high_risk,
        "averageNoShowRisk": avg_risk,
        "averageUtilization": avg_utilization,
        "todayNoShows": db.query(Appointment).filter(Appointment.status == "NO_SHOW").count()
    }

@router.get("/analytics/risk")
def get_risk_distribution(db: Session = Depends(get_db)):
    low = db.query(Appointment).filter(Appointment.risk == "LOW").count()
    medium = db.query(Appointment).filter(Appointment.risk == "MEDIUM").count()
    high = db.query(Appointment).filter(Appointment.risk == "HIGH").count()
    return {"low": low, "medium": medium, "high": high}

@router.get("/analytics/departments")
def get_department_analytics(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    depts = {}
    for doc in doctors:
        dept = doc.department
        if dept not in depts:
            depts[dept] = {"department": dept, "doctorsCount": 0, "totalUtilization": 0}
        depts[dept]["doctorsCount"] += 1
        depts[dept]["totalUtilization"] += doc.utilization

    return [
        {
            "department": k,
            "doctorsCount": v["doctorsCount"],
            "averageUtilization": round(v["totalUtilization"] / v["doctorsCount"], 1)
        }
        for k, v in depts.items()
    ]

@router.get("/notifications")
def get_notifications(db: Session = Depends(get_db)):
    notes = db.query(Notification).order_by(Notification.created_at.desc()).all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "detail": n.detail,
            "tone": n.tone,
            "isRead": n.is_read,
            "time": n.time
        }
        for n in notes
    ]

@router.put("/notifications/{id}/read")
def mark_notification_read(id: str, db: Session = Depends(get_db)):
    note = db.query(Notification).filter(Notification.id == id).first()
    if note:
        note.is_read = True
        db.commit()
    return {"status": "ok", "id": id}

@router.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(50).all()
    return [
        {
            "id": l.id,
            "action": l.action,
            "performedBy": l.performed_by,
            "details": l.details,
            "timestamp": l.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for l in logs
    ]
