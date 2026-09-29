import streamlit as st
import pandas as pd

from core.model_engine import load_reference_data


# ============================================================
# PAGE
# ============================================================

st.title("Twin Overview")

st.caption(
    "Overview of the stroke digital twin cohort, active patient state, "
    "clinical journey and AI-supported predictions."
)


# ============================================================
# LOAD COHORT
# ============================================================

try:
    df = load_reference_data()
except Exception:
    df = pd.DataFrame()


# ============================================================
# SESSION STATE
# ============================================================

patient = st.session_state.get("patient")
patient_id = st.session_state.get("patient_id")

stage = st.session_state.get(
    "twin_stage",
    "Admission"
)

ht_probability = st.session_state.get(
    "ht_probability"
)

ht_risk_label = st.session_state.get(
    "ht_risk_label"
)

model_status = st.session_state.get(
    "model_status",
    "Ready"
)


# ============================================================
# HELPERS
# ============================================================

def get_value(field, default="—"):

    if patient is None:
        return default

    if field not in patient.index:
        return default

    value = patient[field]

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return value


def yes_no(field):

    value = get_value(field, None)

    if value == 1:
        return "Yes"

    if value == 0:
        return "No"

    return "—"


# ============================================================
# SYSTEM OVERVIEW
# ============================================================

st.markdown("## Digital Twin Status")


c1, c2, c3, c4 = st.columns(4)


# Cohort size
if df is not None and not df.empty:
    cohort_size = len(df)
else:
    cohort_size = "—"


c1.metric(
    "Synthetic Cohort",
    cohort_size,
    help="Number of synthetic stroke patient records available."
)


c2.metric(
    "Active Patient",
    patient_id if patient_id else "None"
)


c3.metric(
    "Current Stage",
    stage if patient_id else "—"
)


c4.metric(
    "AI Model Status",
    model_status
)


# ============================================================
# NO ACTIVE PATIENT
# ============================================================

if patient is None or patient.empty:

    st.info(
        "No active patient digital twin. "
        "Open Patient Digital Twin and select a patient."
    )

    st.markdown("## Digital Twin Workflow")

    st.write(
        "The platform follows the patient from admission through "
        "treatment, hospital course and follow-up while updating "
        "AI predictions and clinical intelligence as new information "
        "becomes available."
    )

    st.stop()


# ============================================================
# ACTIVE PATIENT
# ============================================================

st.markdown("---")

st.markdown(
    f"## Active Patient · {patient_id}"
)

st.caption(
    f"Current longitudinal twin state: {stage}"
)


# ============================================================
# BASIC PATIENT SNAPSHOT
# ============================================================

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Age",
    get_value("age")
)


c2.metric(
    "Sex",
    get_value("sex")
)


c3.metric(
    "Baseline NIHSS",
    get_value("baseline_nihss")
)


c4.metric(
    "ASPECTS",
    get_value("aspects")
)


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Systolic BP",
    get_value("systolic_bp")
)


c2.metric(
    "Diastolic BP",
    get_value("diastolic_bp")
)


c3.metric(
    "Admission Glucose",
    get_value("admission_glucose_mmol_l")
)


c4.metric(
    "Pre-stroke mRS",
    get_value("prestroke_mrs")
)


# ============================================================
# CLINICAL JOURNEY
# ============================================================

st.markdown("## Patient Journey")


STAGES = [
    "Admission",
    "Treatment",
    "Hospital Course",
    "Discharge & Follow-Up"
]


current_index = STAGES.index(stage) if stage in STAGES else 0


journey_cols = st.columns(4)


for i, stage_name in enumerate(STAGES):

    with journey_cols[i]:

        if i < current_index:

            st.success(
                f"✓ {stage_name}"
            )

        elif i == current_index:

            st.info(
                f"● {stage_name}"
            )

        else:

            st.write(
                f"○ {stage_name}"
            )


# ============================================================
# CURRENT CLINICAL STATE
# ============================================================

st.markdown("## Current Clinical State")


if stage == "Admission":

    st.write(
        "The patient is currently represented using baseline "
        "admission information. Treatment and subsequent outcomes "
        "have not yet been revealed to the digital twin."
    )


elif stage == "Treatment":

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "IV Thrombolysis",
        yes_no("iv_thrombolysis")
    )

    c2.metric(
        "Mechanical Thrombectomy",
        yes_no("mechanical_thrombectomy")
    )

    c3.metric(
        "HT Risk Assessment",
        "Available"
    )


elif stage == "Hospital Course":

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Observed HT",
        yes_no("hemorrhagic_transformation")
    )

    c2.metric(
        "Symptomatic ICH",
        yes_no("symptomatic_ich")
    )

    c3.metric(
        "Recanalisation",
        get_value("recanalization_status")
    )


elif stage == "Discharge & Follow-Up":

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Discharge mRS",
        get_value("discharge_mrs")
    )

    c2.metric(
        "90-Day mRS",
        get_value("mrs_90d")
    )

    c3.metric(
        "90-Day Mortality",
        yes_no("mortality_90d")
    )


# ============================================================
# AI INTELLIGENCE
# ============================================================

st.markdown("## AI Intelligence")


c1, c2, c3 = st.columns(3)


# HT probability
if ht_probability is not None:

    try:
        probability_display = (
            f"{float(ht_probability) * 100:.1f}%"
        )
    except Exception:
        probability_display = str(ht_probability)

else:
    probability_display = "Not calculated"


c1.metric(
    "Predicted HT Risk",
    probability_display
)


c2.metric(
    "HT Risk Category",
    ht_risk_label
    if ht_risk_label
    else "Pending"
)


recommendation = st.session_state.get(
    "current_recommendation"
)


c3.metric(
    "Clinical Recommendation",
    "Generated"
    if recommendation
    else "Pending"
)


# ============================================================
# MODEL / ASSURANCE STATUS
# ============================================================

st.markdown("## AI Assurance")


c1, c2, c3 = st.columns(3)


c1.metric(
    "HT Model",
    st.session_state.get(
        "model_version",
        "M1 HT Risk"
    )
)


c2.metric(
    "Model Status",
    model_status
)


adaptation_status = st.session_state.get(
    "adaptation_status",
    "Not assessed"
)


c3.metric(
    "Adaptation Status",
    adaptation_status
)


# ============================================================
# NEXT ACTION
# ============================================================

st.markdown("---")


if stage == "Admission":

    st.info(
        "Next: advance the digital twin to Treatment in "
        "Patient Journey."
    )

elif stage == "Treatment":

    if ht_probability is None:

        st.info(
            "Next: run HT Risk & Explanation to estimate "
            "hemorrhagic transformation risk."
        )

    else:

        st.success(
            "HT risk has been estimated. Continue with What-If "
            "Explorer, Clinical Recommendations, or advance the "
            "patient journey."
        )

elif stage == "Hospital Course":

    st.info(
        "New post-treatment observations are available. "
        "The twin can now compare predicted risk with the "
        "observed clinical course."
    )

else:

    st.success(
        "The longitudinal digital twin has reached the "
        "Discharge & Follow-Up stage."
    )