from sqlalchemy.orm import Session
from models import User, Doctor, Appointment, Waitlist, Notification
import hashlib

def hash_pw(password: str) -> str:
    # Use sha256 with salt for lightweight dependency-safe password storage
    return hashlib.sha256(f"carepilot_salt_{password}".encode()).hexdigest()

def seed_database(db: Session):
    # Only seed if users table is empty
    if db.query(User).first() is not None:
        return

    # Seed Admin & Demo Patients
    admin = User(
        id="ADM-01",
        email="admin@carepilot.hospital",
        password_hash=hash_pw("admin123"),
        full_name="Dr. Sarah Jenkins",
        phone="+1 (555) 019-2831",
        role="admin",
        age=42,
        gender="Female"
    )

    patient1 = User(
        id="P001",
        email="demo.patient@example.test",
        password_hash=hash_pw("patient123"),
        full_name="Demo Patient",
        phone="+1 (555) 234-5678",
        role="patient",
        age=34,
        gender="Male"
    )

    patient2 = User(
        id="P002",
        email="demo.patient2@example.test",
        password_hash=hash_pw("patient123"),
        full_name="Demo Patient 2",
        phone="+1 (555) 345-6789",
        role="patient",
        age=45,
        gender="Female"
    )

    db.add_all([admin, patient1, patient2])

    # Seed Doctors
    doctors = [
        Doctor(id="D001", name="Dr. Kumar", department="Cardiology", specialization="Interventional Cardiology", room="Room 302", hours="09:00 AM – 04:00 PM", appointments=18, completed=12, cancelled=1, high_risk=3, utilization=82),
        Doctor(id="D002", name="Dr. Mehta", department="Neurology", specialization="Clinical Neurology", room="Room 405", hours="09:30 AM – 03:30 PM", appointments=14, completed=10, cancelled=2, high_risk=2, utilization=76),
        Doctor(id="D003", name="Dr. Shah", department="Pediatrics", specialization="Pediatric Care", room="Room 108", hours="08:30 AM – 02:00 PM", appointments=12, completed=9, cancelled=1, high_risk=1, utilization=68),
        Doctor(id="D004", name="Dr. Rao", department="Orthopedics", specialization="Sports Orthopedics", room="Room 210", hours="10:00 AM – 05:00 PM", appointments=11, completed=8, cancelled=1, high_risk=1, utilization=61),
    ]
    db.add_all(doctors)

    # Seed Initial Appointments
    appointments = [
        Appointment(id="A001", patient_id="P001", patient="Demo Patient", doctor="Dr. Kumar", department="Cardiology", date="2026-09-03", time="10:30 AM", type="Consultation", probability=72, risk="HIGH", status="PENDING", notes="Patient reported high blood pressure episodes."),
        Appointment(id="A002", patient_id="P002", patient="Demo Patient 2", doctor="Dr. Mehta", department="Neurology", date="2026-09-03", time="11:00 AM", type="Follow-up", probability=48, risk="MEDIUM", status="CONFIRMED", notes="Routine EEG review."),
        Appointment(id="A003", patient_id="P003", patient="Demo Patient 3", doctor="Dr. Shah", department="Pediatrics", date="2026-09-03", time="11:30 AM", type="Consultation", probability=18, risk="LOW", status="CONFIRMED", notes="Annual vaccination check."),
        Appointment(id="A004", patient_id="P004", patient="Demo Patient 4", doctor="Dr. Kumar", department="Cardiology", date="2026-09-03", time="12:00 PM", type="New patient", probability=56, risk="MEDIUM", status="PENDING", notes="Referral from family physician."),
        Appointment(id="A005", patient_id="P005", patient="Demo Patient 5", doctor="Dr. Rao", department="Orthopedics", date="2026-09-04", time="09:00 AM", type="Consultation", probability=29, risk="LOW", status="CONFIRMED", notes="Knee sprain examination."),
    ]
    db.add_all(appointments)

    # Seed Waitlist
    waitlist = [
        Waitlist(id="W001", patient_id="P006", patient="Demo Patient 6", doctor="Dr. Kumar", department="Cardiology", date="2026-09-03", time="10:30 AM", priority="HIGH", status="WAITING"),
        Waitlist(id="W002", patient_id="P007", patient="Demo Patient 7", doctor="Dr. Mehta", department="Neurology", date="2026-09-03", time="11:00 AM", priority="MEDIUM", status="WAITING"),
        Waitlist(id="W003", patient_id="P008", patient="Demo Patient 8", doctor="Dr. Kumar", department="Cardiology", date="2026-09-04", time="09:00 AM", priority="LOW", status="WAITING"),
        Waitlist(id="W004", patient_id="P009", patient="Demo Patient 9", doctor="Dr. Shah", department="Pediatrics", date="2026-09-04", time="11:30 AM", priority="MEDIUM", status="SLOT_OFFERED"),
    ]
    db.add_all(waitlist)

    # Seed Notifications
    notifications = [
        Notification(id="N001", title="High-risk appointments need attention", detail="2 appointments have elevated no-show risk.", tone="high", time="Now"),
        Notification(id="N002", title="Pending confirmations", detail="2 patients have not confirmed.", tone="pending", time="Today"),
        Notification(id="N003", title="Waitlist ready for slot offers", detail="3 patients are waiting for availability.", tone="waitlist", time="Today"),
    ]
    db.add_all(notifications)

    db.commit()
