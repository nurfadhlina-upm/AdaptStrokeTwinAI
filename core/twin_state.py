import pandas as pd


# ============================================================
# DIGITAL TWIN CLINICAL STAGES
# ============================================================

STAGES = [
    "Admission",
    "Treatment",
    "Hospital Course",
    "Discharge & Follow-Up"
]


# ============================================================
# VARIABLES AVAILABLE AT EACH STAGE
#
# IMPORTANT:
# These lists control temporal visibility.
# A variable becomes available only when its clinical stage
# has been reached.
# ============================================================

ADMISSION_FIELDS = [

    # Identity
    "stroke_id",
    "patient_id",
    "Patient_ID",
    "id",

    # Demographics
    "age",
    "sex",

    # Baseline stroke state
    "baseline_nihss",
    "aspects",
    "prestroke_mrs",

    # Admission physiology
    "systolic_bp",
    "diastolic_bp",
    "admission_glucose_mmol_l",

    # Timing / presentation
    "onset_to_door_min",

    # Common baseline clinical variables
    "hypertension",
    "diabetes",
    "atrial_fibrillation",
    "previous_stroke",
    "smoking"
]


TREATMENT_FIELDS = [

    # Reperfusion treatment
    "iv_thrombolysis",
    "mechanical_thrombectomy",

    # Treatment timing
    "door_to_needle_min",
    "door_to_puncture_min",

    # Other treatment-related variables if present
    "thrombolytic_agent",
    "occlusion_site"
]


HOSPITAL_FIELDS = [

    # Observed post-treatment events
    "hemorrhagic_transformation",
    "symptomatic_ich",

    # Treatment response
    "recanalization_status",
    "tici_score",

    # Later inpatient observations
    "post_treatment_nihss",
    "nihss_24h"
]


FOLLOWUP_FIELDS = [

    # Discharge
    "discharge_mrs",

    # Follow-up outcomes
    "mrs_90d",
    "mortality_90d"
]


# ============================================================
# HELPERS
# ============================================================

def _valid_value(value):
    """
    Return False for missing/NaN values.
    """

    try:
        return not pd.isna(value)
    except Exception:
        return value is not None


def _copy_available_fields(record, fields):
    """
    Copy only fields that actually exist in the CSV.
    """

    state = {}

    for field in fields:

        if field in record.index:

            value = record[field]

            if _valid_value(value):
                state[field] = value

    return state


# ============================================================
# BUILD CURRENT DIGITAL TWIN STATE
# ============================================================

def build_patient_state(record, stage):
    """
    Construct the patient state that is clinically available
    at the requested stage.

    The complete synthetic patient record remains hidden in
    patient_record.

    Only temporally available variables are returned here.
    """

    if record is None:
        return None


    state = {}


    # --------------------------------------------------------
    # ADMISSION
    # --------------------------------------------------------

    state.update(
        _copy_available_fields(
            record,
            ADMISSION_FIELDS
        )
    )


    # --------------------------------------------------------
    # TREATMENT
    # --------------------------------------------------------

    if stage in [
        "Treatment",
        "Hospital Course",
        "Discharge & Follow-Up"
    ]:

        state.update(
            _copy_available_fields(
                record,
                TREATMENT_FIELDS
            )
        )


    # --------------------------------------------------------
    # HOSPITAL COURSE
    # --------------------------------------------------------

    if stage in [
        "Hospital Course",
        "Discharge & Follow-Up"
    ]:

        state.update(
            _copy_available_fields(
                record,
                HOSPITAL_FIELDS
            )
        )


    # --------------------------------------------------------
    # DISCHARGE / FOLLOW-UP
    # --------------------------------------------------------

    if stage == "Discharge & Follow-Up":

        state.update(
            _copy_available_fields(
                record,
                FOLLOWUP_FIELDS
            )
        )


    return pd.Series(state)


# ============================================================
# SYNCHRONISE SESSION STATE
# ============================================================

def sync_twin_state(session_state):
    """
    Rebuild the active patient state whenever the digital
    twin moves to another clinical stage.
    """

    record = session_state.get(
        "patient_record"
    )

    stage = session_state.get(
        "twin_stage",
        "Admission"
    )


    if record is None:
        session_state.patient = None
        return None


    patient = build_patient_state(
        record,
        stage
    )


    session_state.patient = patient

    return patient