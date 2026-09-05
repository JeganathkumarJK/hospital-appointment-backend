from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=True)
    role = Column(String(20), default="patient") # 'patient', 'admin', 'doctor'
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String(50), primary_key=True, index=True)
    patient_id = Column(String(50), index=True, nullable=False)
    patient = Column(String(100), nullable=False)
    doctor = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    date = Column(String(20), nullable=False, index=True) # YYYY-MM-DD
    time = Column(String(20), nullable=False) # e.g. "10:30 AM"
    type = Column(String(50), default="Consultation")
    probability = Column(Integer, default=20) # 0 - 100 AI predicted no-show %
    risk = Column(String(20), default="LOW") # 'LOW', 'MEDIUM', 'HIGH'
    status = Column(String(30), default="PENDING") # PENDING, CONFIRMED, CHECKED_IN, COMPLETED, CANCELLED, NO_SHOW
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    specialization = Column(String(150), nullable=True)
    room = Column(String(50), nullable=True)
    hours = Column(String(100), default="09:00 AM – 04:00 PM")
    appointments = Column(Integer, default=0)
    completed = Column(Integer, default=0)
    cancelled = Column(Integer, default=0)
    high_risk = Column(Integer, default=0)
    utilization = Column(Integer, default=70) # percentage

class Waitlist(Base):
    __tablename__ = "waitlists"

    id = Column(String(50), primary_key=True, index=True)
    patient_id = Column(String(50), nullable=False)
    patient = Column(String(100), nullable=False)
    doctor = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    date = Column(String(20), nullable=False)
    time = Column(String(20), nullable=False)
    priority = Column(String(20), default="MEDIUM") # HIGH, MEDIUM, LOW
    status = Column(String(30), default="WAITING") # WAITING, SLOT_OFFERED, ACCEPTED, DECLINED
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), nullable=True) # None = broadcast to all staff
    title = Column(String(200), nullable=False)
    detail = Column(Text, nullable=False)
    tone = Column(String(30), default="info") # high, pending, waitlist, info
    is_read = Column(Boolean, default=False)
    time = Column(String(50), default="Just now")
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100), nullable=False)
    performed_by = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
