from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User, LoginLog, Appointment, Waitlist
from schemas import UserRegister, UserLogin, UserResponse
from seed_data import hash_pw
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register_user(data: UserRegister, db: Session = Depends(get_db)):
    # Check if email already registered
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Generate sequential patient ID: P001, P002...
    user_count = db.query(User).filter(User.role == "patient").count()
    patient_id = f"P{str(user_count + 1).zfill(3)}"

    new_user = User(
        id=patient_id,
        email=data.email.lower(),
        password_hash=hash_pw(data.password),
        full_name=data.fullName,
        phone=data.phone,
        role=data.role or "patient",
        age=data.age,
        gender=data.gender
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        name=new_user.full_name,
        email=new_user.email,
        phone=new_user.phone,
        role=new_user.role,
        title="Registered Patient"
    )

@router.post("/login", response_model=UserResponse)
def login_user(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    query = data.identifier.strip().lower()
    hashed = hash_pw(data.password)

    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:250]

    # Find by email or ID
    user = db.query(User).filter(
        (User.email.ilike(query)) | (User.id.ilike(query))
    ).first()

    if not user or user.password_hash != hashed:
        # Record failed login attempt
        failed_log = LoginLog(
            user_id=user.id if user else None,
            email=query,
            full_name=user.full_name if user else "Unknown Attempt",
            role=user.role if user else "guest",
            status="FAILED",
            ip_address=client_ip,
            user_agent=user_agent
        )
        db.add(failed_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your email/ID and password."
        )

    # Update user login metadata
    user.last_login = datetime.utcnow()
    user.login_count = (user.login_count or 0) + 1

    # Record successful login attempt
    success_log = LoginLog(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        status="SUCCESS",
        ip_address=client_ip,
        user_agent=user_agent
    )
    db.add(success_log)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        title="Hospital Administrator" if user.role == "admin" else "Registered Patient",
        department="Executive Staff" if user.role == "admin" else None
    )

@router.get("/patients")
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(User).filter(User.role == "patient").all()
    return [
        {
            "id": p.id,
            "name": p.full_name,
            "contact": p.email,
            "phone": p.phone,
            "age": p.age,
            "gender": p.gender,
            "joined": p.created_at.strftime("%Y-%m-%d") if p.created_at else "2026-09-01",
            "lastLogin": p.last_login.strftime("%Y-%m-%d %H:%M:%S") if p.last_login else "Never",
            "loginCount": p.login_count or 0
        }
        for p in patients
    ]

@router.get("/users")
def list_all_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "fullName": u.full_name,
            "phone": u.phone,
            "role": u.role,
            "age": u.age,
            "gender": u.gender,
            "lastLogin": u.last_login.strftime("%Y-%m-%d %H:%M:%S") if u.last_login else "Never",
            "loginCount": u.login_count or 0,
            "joined": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else "2026-09-01 00:00:00"
        }
        for u in users
    ]

@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    deleted_name = user.full_name
    deleted_role = user.role

    # Clean up associated patient appointments & waitlist records
    db.query(Appointment).filter(Appointment.patient_id == user_id).delete()
    db.query(Waitlist).filter(Waitlist.patient_id == user_id).delete()
    db.query(LoginLog).filter(LoginLog.user_id == user_id).delete()

    db.delete(user)
    db.commit()

    return {
        "status": "success",
        "message": f"{deleted_role.capitalize()} '{deleted_name}' (ID: {user_id}) and related records deleted successfully.",
        "deletedUserId": user_id
    }

@router.get("/login-history")
def get_login_history(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(LoginLog).order_by(LoginLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "userId": l.user_id,
            "email": l.email,
            "fullName": l.full_name,
            "role": l.role,
            "status": l.status,
            "ipAddress": l.ip_address,
            "userAgent": l.user_agent,
            "timestamp": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "Just now"
        }
        for l in logs
    ]

@router.delete("/login-history/{log_id}")
def delete_login_log(log_id: int, db: Session = Depends(get_db)):
    log_item = db.query(LoginLog).filter(LoginLog.id == log_id).first()
    if not log_item:
        raise HTTPException(status_code=404, detail="Log entry not found")
    db.delete(log_item)
    db.commit()
    return {"status": "success", "message": f"Log entry #{log_id} deleted"}

@router.delete("/login-history")
def clear_all_login_history(db: Session = Depends(get_db)):
    deleted_count = db.query(LoginLog).delete()
    db.commit()
    return {"status": "success", "message": f"Cleared {deleted_count} login log records"}
