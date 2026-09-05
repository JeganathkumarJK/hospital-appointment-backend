from fastapi import APIRouter
from schemas import PredictRequest, PredictResponse
from ml_model import ai_engine
import datetime

router = APIRouter(tags=["AI Prediction Engine"])

@router.post("/predict-no-show", response_model=PredictResponse)
def predict_no_show_risk(data: PredictRequest):
    # Compute lead time if appointment_date provided
    lead_time = data.lead_time_days if data.lead_time_days is not None else 3
    if data.appointment_date:
        try:
            target_dt = datetime.datetime.strptime(data.appointment_date, "%Y-%m-%d").date()
            today = datetime.date.today()
            lead_time = max(0, (target_dt - today).days)
        except Exception:
            lead_time = 3

    prediction = ai_engine.predict(
        lead_time_days=lead_time,
        age=data.age or 35,
        prior_no_shows=data.prior_no_shows or 0,
        department=data.department or "General",
        appointment_date=data.appointment_date,
        sms_sent=data.sms_reminder_sent if data.sms_reminder_sent is not None else True
    )

    return PredictResponse(
        appointment_id=data.appointment_id,
        no_show_probability=prediction["no_show_probability"],
        risk_level=prediction["risk_level"],
        recommended_action=prediction["recommended_action"],
        confidence_score=prediction["confidence_score"],
        factors=prediction["factors"]
    )
