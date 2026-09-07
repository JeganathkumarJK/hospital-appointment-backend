from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserRegister, UserLogin, UserResponse
from seed_data import hash_pw

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
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    query = data.identifier.strip().lower()
    hashed = hash_pw(data.password)

    # Find by email or ID
    user = db.query(User).filter(
        (User.email.ilike(query)) | (User.id.ilike(query))
    ).first()

    if not user or user.password_hash != hashed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your email/ID and password."
        )

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
            "joined": p.created_at.strftime("%Y-%m-%d") if p.created_at else "2026-09-01"
        }
        for p in patients
    ]

@router.get("/users")
def list_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "fullName": u.full_name,
            "phone": u.phone,
            "role": u.role,
            "age": u.age,
            "gender": u.gender,
            "joined": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else "2026-09-01 00:00:00"
        }
        for u in users
    ]
