import streamlit as st
import pandas as pd

from core.twin_state import (
    STAGES,
    sync_twin_state
)

st.title("Patient Journey")

st.caption(
    "Advance the patient digital twin as new clinical "
    "information becomes available during the stroke journey."
)


# ============================================================
# CHECK PATIENT
# ============================================================

record = st.session_state.get("patient_record")

if record is None:

    st.info(
        "Select a patient in Patient Digital Twin first."
    )

    st.stop()


# ============================================================
# STAGES
# ============================================================

stage_index = st.session_state.get(
    "twin_stage_index",
    0
)


current_stage = STAGES[
    stage_index
]


st.session_state.twin_stage = (
    current_stage
)


# ============================================================
# HELPER
# ============================================================

def value(field, default="—"):

    if field not in record.index:
        return default

    result = record[field]

    try:
        if pd.isna(result):
            return default
    except Exception:
        pass

    return result


# ============================================================
# JOURNEY HEADER
# ============================================================

st.markdown("## Digital Twin Journey")


cols = st.columns(4)


for i, stage in enumerate(STAGES):

    with cols[i]:

        if i < stage_index:

            st.success(
                f"✓ {stage}"
            )

        elif i == stage_index:

            st.info(
                f"● {stage}"
            )

        else:

            st.write(
                f"○ {stage}"
            )


st.markdown("---")


# ============================================================
# CURRENT STAGE
# ============================================================

st.markdown(
    f"## Current State · {current_stage}"
)


# ============================================================
# ADMISSION
# ============================================================

if current_stage == "Admission":

    st.write(
        "The patient has entered the stroke pathway. "
        "Only information available at admission is shown."
    )


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "Age",
        value("age")
    )

    c2.metric(
        "NIHSS",
        value("baseline_nihss")
    )

    c3.metric(
        "ASPECTS",
        value("aspects")
    )

    c4.metric(
        "Systolic BP",
        value("systolic_bp")
    )


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "Glucose",
        value(
            "admission_glucose_mmol_l"
        )
    )

    c2.metric(
        "Onset-to-door",
        value(
            "onset_to_door_min"
        )
    )

    c3.metric(
        "Pre-stroke mRS",
        value(
            "prestroke_mrs"
        )
    )


# ============================================================
# TREATMENT
# ============================================================

elif current_stage == "Treatment":

    st.write(
        "Treatment information has now become available. "
        "The HT prediction model can update the twin."
    )


    c1, c2, c3, c4 = st.columns(4)


    ivt = value(
        "iv_thrombolysis",
        0
    )


    mt = value(
        "mechanical_thrombectomy",
        0
    )


    c1.metric(
        "IV Thrombolysis",
        "Yes" if ivt == 1 else "No"
    )


    c2.metric(
        "Door-to-needle",
        (
            f"{value('door_to_needle_min')} min"
            if ivt == 1
            else "N/A"
        )
    )


    c3.metric(
        "Thrombectomy",
        "Yes" if mt == 1 else "No"
    )


    c4.metric(
        "HT Model",
        "Available"
    )


# ============================================================
# HOSPITAL COURSE
# ============================================================

elif current_stage == "Hospital Course":

    st.write(
        "Post-treatment observations are now available "
        "and synchronised with the patient twin."
    )


    c1, c2, c3 = st.columns(3)


    ht = value(
        "hemorrhagic_transformation",
        "—"
    )


    sich = value(
        "symptomatic_ich",
        "—"
    )


    recan = value(
        "recanalization_status",
        "—"
    )


    c1.metric(
        "Observed HT",
        (
            "Yes" if ht == 1
            else "No" if ht == 0
            else "—"
        )
    )


    c2.metric(
        "sICH",
        (
            "Yes" if sich == 1
            else "No" if sich == 0
            else "—"
        )
    )


    c3.metric(
        "Recanalisation",
        recan
    )


    st.success(
        "New hospital-course information is now "
        "available to the updated outcome model."
    )


# ============================================================
# DISCHARGE / FOLLOW-UP
# ============================================================

elif current_stage == "Discharge & Follow-Up":

    st.write(
        "The patient twin now contains the later clinical "
        "state required for outcome assessment."
    )


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "Discharge mRS",
        value(
            "discharge_mrs"
        )
    )


    c2.metric(
        "90-Day mRS",
        value(
            "mrs_90d"
        )
    )


    mortality = value(
        "mortality_90d",
        "—"
    )


    c3.metric(
        "90-Day Mortality",
        (
            "Yes"
            if mortality == 1
            else "No"
            if mortality == 0
            else "—"
        )
    )


# ============================================================
# ADVANCE
# ============================================================

st.markdown("---")


if stage_index < len(STAGES) - 1:

    next_stage = STAGES[
        stage_index + 1
    ]


    st.caption(
        f"Next clinical state: {next_stage}"
    )

    if st.button(
            f"Advance Twin to {next_stage}",
            type="primary",
            use_container_width=True
    ):
        # Move journey forward
        st.session_state.twin_stage_index += 1

        new_stage = STAGES[
            st.session_state.twin_stage_index
        ]

        st.session_state.twin_stage = new_stage

        # ========================================================
        # SYNCHRONISE DIGITAL TWIN
        # ========================================================

        sync_twin_state(
            st.session_state
        )

        # ========================================================
        # INVALIDATE RESULTS FROM PREVIOUS STATE
        # ========================================================

        st.session_state.predictions = None

        st.session_state.current_recommendation = None

        st.session_state.counterfactual_result = None

        # ========================================================
        # RECORD TWIN EVENT
        # ========================================================

        st.session_state.twin_history.append({

            "event": "Clinical state advanced",

            "stage": new_stage

        })

        st.rerun()

        st.session_state[
            "twin_stage_index"
        ] += 1


        st.session_state.twin_stage = (
            STAGES[
                st.session_state[
                    "twin_stage_index"
                ]
            ]
        )


        # Clear recommendation because
        # patient context has changed

        st.session_state[
            "current_recommendation"
        ] = None


        st.rerun()


else:

    st.success(
        "The patient has reached the final stage "
        "of this digital twin simulation."
    )


# ============================================================
# RESET FOR DEMONSTRATION
# ============================================================

st.markdown("### Simulation Control")


if st.button(
    "Restart Patient Journey"
):

    st.session_state[
        "twin_stage_index"
    ] = 0

    st.session_state[
        "twin_stage"
    ] = "Admission"

    # Return twin to admission information only
    sync_twin_state(
        st.session_state
    )

    # Clear downstream analyses
    st.session_state.ht_probability = None
    st.session_state.ht_risk_label = None
    st.session_state.ht_explanation = None

    st.session_state.predictions = None

    st.session_state.counterfactual_result = None

    st.session_state.current_recommendation = None

    st.session_state.twin_history = []

    st.rerun()