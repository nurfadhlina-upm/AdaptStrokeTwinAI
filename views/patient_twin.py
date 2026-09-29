from core.twin_state import build_patient_state
import streamlit as st
import pandas as pd

from core.model_engine import load_reference_data


# ============================================================
# PAGE
# ============================================================

st.title("Patient Digital Twin")

st.caption(
    "Select a patient from the synthetic ASEAN stroke cohort "
    "to initialise the longitudinal digital twin."
)


# ============================================================
# LOAD SYNTHETIC DATA
# ============================================================

df = load_reference_data()

if df is None or df.empty:
    st.error("The synthetic stroke dataset could not be loaded.")
    st.stop()


# ============================================================
# IDENTIFY PATIENT ID COLUMN
# ============================================================

possible_id_columns = [
    "stroke_id",
    "patient_id",
    "Patient_ID",
    "id"
]

id_column = None

for col in possible_id_columns:
    if col in df.columns:
        id_column = col
        break


if id_column is None:
    st.error(
        "No patient ID column was found in the synthetic dataset."
    )
    st.stop()


# ============================================================
# PATIENT IDS
# ============================================================

patient_ids = df[id_column].astype(str).tolist()


# ============================================================
# CURRENT SELECTION
# ============================================================

current_patient_id = st.session_state.get("patient_id")

if current_patient_id in patient_ids:
    default_index = patient_ids.index(current_patient_id)
else:
    default_index = 0


# ============================================================
# SELECT PATIENT
# ============================================================

st.markdown("## Select Patient")

selected_id = st.selectbox(
    "Patient Twin ID",
    patient_ids,
    index=default_index
)


# ============================================================
# GET SELECTED PATIENT
# ============================================================

selected_rows = df[
    df[id_column].astype(str) == selected_id
]


if selected_rows.empty:
    st.error("The selected patient could not be found.")
    st.stop()


selected_patient = selected_rows.iloc[0].copy()


# ============================================================
# AUTOMATICALLY INITIALISE / CHANGE ACTIVE TWIN
# ============================================================

previous_id = st.session_state.get("patient_id")


if previous_id != selected_id:

    # Complete longitudinal record from CSV
    st.session_state.patient_record = selected_patient.copy()

    # Current working twin state
    st.session_state.patient = build_patient_state(
        selected_patient,
        "Admission"
    )

    st.session_state.patient_id = selected_id

    # Start new patient journey at admission
    st.session_state.twin_stage = "Admission"
    st.session_state.twin_stage_index = 0
    st.session_state.twin_history = []

    # Reset model results from previous patient
    st.session_state.ht_probability = None
    st.session_state.ht_risk_label = None
    st.session_state.ht_explanation = None
    st.session_state.predictions = None

    # Reset what-if analysis
    st.session_state.counterfactual_result = None
    st.session_state.counterfactual_clinician_review = None

    # Reset recommendation / LLM state
    st.session_state.current_recommendation = None
    st.session_state.recommendation = None
    st.session_state.recommendation_history = []
    st.session_state.latest_clinical_note = ""

    # Reset HITL feedback
    st.session_state.clinician_feedback = None,

    st.rerun()


# ============================================================
# ENSURE PATIENT RECORD EXISTS
# This handles first run / old session state
# ============================================================

if st.session_state.get("patient_record") is None:

    st.session_state.patient_record = selected_patient.copy()
    st.session_state.patient = build_patient_state(
        selected_patient,
        "Admission"
    )
    st.session_state.patient_id = selected_id
    st.session_state.twin_stage = "Admission"
    st.session_state.twin_stage_index = 0


patient = st.session_state.patient_record


# ============================================================
# HELPER
# ============================================================

def get_value(field, default="—"):

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
# ACTIVE TWIN STATUS
# ============================================================

stage = st.session_state.get(
    "twin_stage",
    "Admission"
)

st.success(
    f"Active Digital Twin: {selected_id}  ·  "
    f"Current Stage: {stage}"
)


# ============================================================
# PATIENT SUMMARY
# ============================================================

st.markdown("## Patient Profile")


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Twin ID",
    selected_id
)

c2.metric(
    "Age",
    get_value("age")
)

c3.metric(
    "Sex",
    get_value("sex")
)

c4.metric(
    "Baseline NIHSS",
    get_value("baseline_nihss")
)


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "ASPECTS",
    get_value("aspects")
)

c2.metric(
    "Systolic BP",
    get_value("systolic_bp")
)

c3.metric(
    "Diastolic BP",
    get_value("diastolic_bp")
)

c4.metric(
    "Admission Glucose",
    get_value("admission_glucose_mmol_l")
)


# ============================================================
# INITIAL TREATMENT PROFILE
# ============================================================

st.markdown("## Treatment Profile")


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
    "Current Twin Stage",
    stage
)


# ============================================================
# COMPLETE SYNTHETIC RECORD
# ============================================================

with st.expander(
    "View Complete Synthetic Patient Record",
    expanded=False
):

    st.caption(
        "This contains the complete synthetic longitudinal record. "
        "Later outcome variables are retained internally for simulation."
    )

    full_patient = pd.DataFrame({
        "Clinical Variable": patient.index,
        "Value": patient.values
    })

    st.dataframe(
        full_patient,
        hide_index=True,
        use_container_width=True
    )


# ============================================================
# NEXT STEP
# ============================================================

st.info(
    "The patient digital twin is active. "
    "Continue to HT Risk & Explanation or Patient Journey."
)