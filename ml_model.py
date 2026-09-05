import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class NoShowPredictionEngine:
    """
    CarePilot AI Prediction Engine for Patient Appointment No-Show Forecasting.
    Uses an ensemble classifier trained on clinical behavioral predictors:
    - Booking lead time (days)
    - Patient age
    - Prior no-show frequency
    - Department urgency factor
    - Day of the week
    - SMS / WhatsApp reminder delivery status
    """

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
        self._train_initial_model()

    def _train_initial_model(self):
        # Feature vector: [lead_time_days, age, prior_no_shows, dept_code, is_weekend_adjacent, sms_sent]
        # dept_code: 0=Cardiology(urgent), 1=Neurology, 2=Pediatrics, 3=Orthopedics, 4=General
        # Target: 0 = Attended, 1 = No-Show

        np.random.seed(42)
        X_train = []
        y_train = []

        # Generate realistic clinical training samples (1,200 rows)
        for _ in range(1200):
            lead_time = int(np.random.exponential(scale=7)) # mostly 1-20 days
            age = int(np.random.uniform(5, 85))
            prior_no_shows = np.random.choice([0, 1, 2, 3], p=[0.75, 0.15, 0.07, 0.03])
            dept_code = np.random.randint(0, 5)
            is_weekend_adjacent = np.random.choice([0, 1], p=[0.6, 0.4]) # Mon/Fri
            sms_sent = np.random.choice([0, 1], p=[0.25, 0.75])

            # Clinical risk formula to assign ground-truth labels
            base_risk = 0.15
            if lead_time > 10:
                base_risk += 0.25
            elif lead_time > 5:
                base_risk += 0.12

            if prior_no_shows > 1:
                base_risk += 0.35
            elif prior_no_shows == 1:
                base_risk += 0.18

            if age < 30:
                base_risk += 0.08
            elif age > 65:
                base_risk -= 0.06

            if is_weekend_adjacent:
                base_risk += 0.08

            if sms_sent == 1:
                base_risk -= 0.15

            # Department factors
            if dept_code in [0, 1]: # Cardiology / Neurology = critical
                base_risk -= 0.10
            elif dept_code == 4: # General
                base_risk += 0.05

            risk_prob = np.clip(base_risk, 0.05, 0.95)
            label = 1 if np.random.rand() < risk_prob else 0

            X_train.append([lead_time, age, prior_no_shows, dept_code, is_weekend_adjacent, sms_sent])
            y_train.append(label)

        self.model.fit(X_train, y_train)

    def _dept_to_code(self, dept: str) -> int:
        d = (dept or "").lower()
        if "cardio" in d:
            return 0
        elif "neuro" in d:
            return 1
        elif "pediatric" in d:
            return 2
        elif "ortho" in d:
            return 3
        return 4

    def predict(
        self,
        lead_time_days: int = 3,
        age: int = 35,
        prior_no_shows: int = 0,
        department: str = "General",
        appointment_date: str = None,
        sms_sent: bool = True
    ) -> dict:
        dept_code = self._dept_to_code(department)

        # Detect Monday or Friday
        is_weekend_adjacent = 0
        if appointment_date:
            try:
                dt = datetime.datetime.strptime(appointment_date, "%Y-%m-%d")
                if dt.weekday() in (0, 4): # Mon or Fri
                    is_weekend_adjacent = 1
            except Exception:
                is_weekend_adjacent = 0

        features = [[
            lead_time_days,
            age,
            prior_no_shows,
            dept_code,
            is_weekend_adjacent,
            1 if sms_sent else 0
        ]]

        probs = self.model.predict_proba(features)[0]
        no_show_prob = float(probs[1]) # probability of no-show (class 1)

        # Risk Classification & Explainable Clinical Factors
        factors = []
        if lead_time_days > 7:
            factors.append(f"Extended booking interval ({lead_time_days} days in advance)")
        if prior_no_shows > 0:
            factors.append(f"Patient has {prior_no_shows} past missed appointment(s)")
        if not sms_sent:
            factors.append("No automated confirmation message sent yet")
        if is_weekend_adjacent:
            factors.append("Appointment is scheduled on a high-attrition day (Monday/Friday)")
        if age < 30:
            factors.append("Demographic age group shows elevated scheduling shifts")

        if no_show_prob >= 0.55:
            risk_level = "HIGH"
            recommendation = (
                "High No-Show Risk: Initiate urgent WhatsApp 2-way confirmation pass. "
                "Flag slot for standby waitlist backfill if unconfirmed 24h prior."
            )
        elif no_show_prob >= 0.30:
            risk_level = "MEDIUM"
            recommendation = (
                "Moderate Risk: Dispatch automated SMS/WhatsApp reminder 48 hours in advance. "
                "Monitor for patient digital check-in."
            )
        else:
            risk_level = "LOW"
            recommendation = (
                "Low Risk: Standard protocol. High probability of on-time patient arrival."
            )

        return {
            "no_show_probability": round(no_show_prob, 2),
            "risk_level": risk_level,
            "recommended_action": recommendation,
            "confidence_score": round(float(np.max(probs)), 2),
            "factors": factors
        }

# Global Singleton Instance
ai_engine = NoShowPredictionEngine()
