from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Auth & User Schemas ---
class UserRegister(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: Optional[str] = "patient"
    age: Optional[int] = None
    gender: Optional[str] = "Other"

class UserLogin(BaseModel):
    identifier: str # Email or patient ID
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    title: Optional[str] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True

# --- Appointment Schemas ---
class AppointmentCreate(BaseModel):
    patientId: Optional[str] = None
    patient: str
    doctor: str
    department: str
    date: str # YYYY-MM-DD
    time: str # "10:30 AM"
    type: Optional[str] = "Consultation"
    notes: Optional[str] = None

class AppointmentReschedule(BaseModel):
    date: str
    time: str

class AppointmentStatusUpdate(BaseModel):
    status: str

class AppointmentResponse(BaseModel):
    id: str
    patientId: str
    patient: str
    doctor: str
    department: str
    date: str
    time: str
    type: str
    probability: int
    risk: str
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# --- Doctor Schemas ---
class DoctorCreate(BaseModel):
    name: str
    department: str
    specialization: Optional[str] = None
    room: Optional[str] = None
    hours: Optional[str] = "09:00 AM – 04:00 PM"

class DoctorResponse(BaseModel):
    id: str
    name: str
    department: str
    specialization: Optional[str] = None
    room: Optional[str] = None
    hours: Optional[str] = None
    appointments: int
    completed: int
    cancelled: int
    highRisk: int
    utilization: int

    class Config:
        from_attributes = True

# --- Waitlist Schemas ---
class WaitlistCreate(BaseModel):
    patientId: str
    patient: str
    doctor: str
    department: str
    date: str
    time: str
    priority: Optional[str] = "MEDIUM"

class WaitlistResponse(BaseModel):
    id: str
    patientId: str
    patient: str
    doctor: str
    department: str
    date: str
    time: str
    priority: str
    status: str

    class Config:
        from_attributes = True

# --- AI Prediction Schemas ---
class PredictRequest(BaseModel):
    appointment_id: Optional[str] = None
    patient_id: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_type: Optional[str] = "Consultation"
    department: Optional[str] = "General"
    age: Optional[int] = 35
    lead_time_days: Optional[int] = 3
    prior_no_shows: Optional[int] = 0
    sms_reminder_sent: Optional[bool] = True

class PredictResponse(BaseModel):
    appointment_id: Optional[str] = None
    no_show_probability: float # 0.0 to 1.0
    risk_level: str # LOW, MEDIUM, HIGH
    recommended_action: str
    confidence_score: float
    factors: List[str] = []

# --- Analytics Schemas ---
class AnalyticsSummary(BaseModel):
    total_appointments: int
    confirmed_count: int
    pending_count: int
    completed_count: int
    high_risk_count: int
    average_no_show_risk: float
    utilization_rate: float
