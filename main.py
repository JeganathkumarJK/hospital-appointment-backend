import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from seed_data import seed_database
from routers import auth, appointments, waitlist, doctors, prediction, analytics

# Create all database tables
Base.metadata.create_all(bind=engine)

# Seed initial records if empty
db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()

app = FastAPI(
    title="CarePilot - AI-Powered Hospital Appointment API",
    description="Intelligent care coordination, no-show predictive ML engine, and slot optimization service.",
    version="1.0.0"
)

# Configure CORS so both localhost and Vercel production frontend can access the API
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://hospital-appointment-frontend-nu.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for production demo flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(waitlist.router)
app.include_router(doctors.router)
app.include_router(prediction.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {
        "service": "CarePilot AI Hospital Appointment Backend",
        "status": "operational",
        "version": "1.0.0",
        "documentation": "/docs",
        "ai_engine": "Scikit-Learn Random Forest Classifier Active",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ai_engine": "ready",
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
