# CarePilot: AI-Powered Hospital Appointment Backend

A high-performance Python FastAPI service with a Scikit-Learn Machine Learning engine for predictive appointment attendance, intelligent waitlist backfills, and full database persistence.

## Features
- **AI / ML Predictive Engine**: Random Forest model trained to forecast patient no-show probabilities (0–100%) and calculate clinical risk levels (`LOW`, `MEDIUM`, `HIGH`).
- **RESTful Endpoints**: Full CRUD and workflows for appointments, physicians, smart waitlists, and hospital KPI analytics.
- **Authentication**: Role-based authentication supporting both Patients and Hospital Administrators.
- **Interactive Documentation**: Built-in Swagger UI at `/docs` and ReDoc at `/redoc`.
- **Cloud-Ready**: Includes `render.yaml`, `Procfile`, and `Dockerfile` for 1-click cloud deployment.

## Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Run Server**:
   ```bash
   python main.py
   # or
   uvicorn main:app --reload --port 8000
   ```

3. **Open Swagger API Docs**:
   Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
