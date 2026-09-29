from core.twin_state import build_patient_state

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.model_engine import (
    predict_binary,
    predict_ht_scenario
)


# ============================================================
# PAGE
# ============================================================

st.title("What-If Explorer")

st.caption(
    "Explore how selected alternative patient states change "
    "the model-estimated risk of hemorrhagic transformation."
)


# ============================================================
# CHECK PATIENT
# ============================================================

patient = st.session_state.get("patient")

if patient is None:

    st.info(
        "No patient twin is currently available. "
        "Open **Patient Digital Twin** and create or load "
        "a patient first."
    )

    st.stop()

# ============================================================
# DIGITAL TWIN STAGE CONTROL
# ============================================================

stage = st.session_state.get(
    "twin_stage",
    "Admission"
)

patient_id = st.session_state.get(
    "patient_id"
)


if stage == "Admission":

    st.info(
        "What-If analysis becomes available after the patient "
        "digital twin reaches the Treatment stage and an HT risk "
        "assessment has been generated."
    )

    st.stop()

# ============================================================
# RECONSTRUCT TREATMENT-STATE TWIN
# ============================================================

patient_record = st.session_state.get(
    "patient_record"
)

if patient_record is None:

    st.error(
        "The complete patient record is unavailable."
    )

    st.stop()


# What-If must always use the same temporal state
# as the original HT prediction.
scenario_patient = build_patient_state(
    patient_record,
    "Treatment"
)

# ============================================================
# HELPER
# ============================================================

def get_value(name, default=None):

    if hasattr(patient, "get"):
        value = patient.get(name, default)

        if pd.isna(value):
            return default

        return value

    return default

# ============================================================
# HEADER METRICS
# ============================================================

st.markdown("### Current Twin")

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Patient",
    st.session_state.get(
        "patient_id"
    ) or "—"
)


c2.metric(
    "Current HT risk",
    f"{current_risk:.1%}"
)


c3.metric(
    "NIHSS",
    get_value(
        "baseline_nihss",
        "—"
    )
)


c4.metric(
    "ASPECTS",
    get_value(
        "aspects",
        "—"
    )
)


# ============================================================
# EXPLANATION
# ============================================================

st.info(
    "This tool changes selected variables while holding "
    "the rest of the patient twin constant. The resulting "
    "difference is a model-based scenario comparison and "
    "should not be interpreted as a causal treatment effect."
)


# ============================================================
# CURRENT VALUES
# ============================================================

current_glucose = float(
    get_value(
        "admission_glucose_mmol_l",
        7.0
    )
)

current_sbp = int(
    get_value(
        "systolic_bp",
        140
    )
)

current_onset = int(
    get_value(
        "onset_to_door_min",
        120
    )
)

ivt = int(
    get_value(
        "iv_thrombolysis",
        0
    )
)

current_dtn = int(
    get_value(
        "door_to_needle_min",
        60
    ) or 0
)


# ============================================================
# SCENARIO BUILDER
# ============================================================

st.markdown("### Build an Alternative Twin")

st.caption(
    "Adjust potentially modifiable or workflow-related "
    "variables to explore another model state."
)


left, right = st.columns(2)


# ------------------------------------------------------------
# METABOLIC / PHYSIOLOGICAL
# ------------------------------------------------------------

with left:

    with st.container(border=True):

        st.markdown(
            "#### Physiological State"
        )

        alt_glucose = st.slider(
            "Admission glucose (mmol/L)",
            min_value=2.0,
            max_value=25.0,
            value=current_glucose,
            step=0.1,
            key="cf_glucose"
        )

        alt_sbp = st.slider(
            "Systolic blood pressure (mmHg)",
            min_value=80,
            max_value=240,
            value=current_sbp,
            step=1,
            key="cf_sbp"
        )

        st.caption(
            "These are alternative model inputs, "
            "not treatment targets."
        )


# ------------------------------------------------------------
# WORKFLOW / TIME
# ------------------------------------------------------------

with right:

    with st.container(border=True):

        st.markdown(
            "#### Care Pathway State"
        )

        alt_onset = st.slider(
            "Onset-to-door time (minutes)",
            min_value=0,
            max_value=720,
            value=current_onset,
            step=5,
            key="cf_onset"
        )


        if ivt == 1:

            alt_dtn = st.slider(
                "Door-to-needle time (minutes)",
                min_value=0,
                max_value=180,
                value=current_dtn,
                step=5,
                key="cf_dtn"
            )

        else:

            alt_dtn = current_dtn

            st.write(
                "**Door-to-needle:** Not applicable"
            )

            st.caption(
                "The current patient twin does not "
                "record IV thrombolysis."
            )


# ============================================================
# CHANGED VARIABLES
# ============================================================

changes = {
    "admission_glucose_mmol_l":
        alt_glucose,

    "systolic_bp":
        alt_sbp,

    "onset_to_door_min":
        alt_onset
}


if ivt == 1:

    changes[
        "door_to_needle_min"
    ] = alt_dtn


# ============================================================
# RUN ALTERNATIVE TWIN
# ============================================================

st.markdown("---")


if st.button(
    "Simulate Alternative Twin",
    type="primary",
    use_container_width=True
):

    try:

        alternative_risk, alternative_patient = (
            predict_ht_scenario(
                spatient,
                changes
            )
        )

        st.session_state[
            "counterfactual_result"
        ] = {

            "current_risk":
                current_risk,

            "alternative_risk":
                alternative_risk,

            "changes":
                changes,

            "alternative_patient":
                alternative_patient
        }

    except Exception as error:

        st.error(
            "The alternative twin could "
            "not be simulated."
        )

        st.exception(error)


# ============================================================
# RESULTS
# ============================================================

result = st.session_state.get(
    "counterfactual_result"
)


if result is not None:

    alt_risk = result[
        "alternative_risk"
    ]

    delta = (
        alt_risk
        - current_risk
    )

    delta_pp = (
        delta * 100
    )


    st.markdown(
        "## Twin Comparison"
    )


    # ========================================================
    # SUMMARY CARDS
    # ========================================================

    c1, c2, c3 = st.columns(3)


    with c1:

        with st.container(
            border=True
        ):

            st.caption(
                "CURRENT TWIN"
            )

            st.metric(
                "HT risk",
                f"{current_risk:.1%}"
            )


    with c2:

        with st.container(
            border=True
        ):

            st.caption(
                "ALTERNATIVE TWIN"
            )

            st.metric(
                "HT risk",
                f"{alt_risk:.1%}"
            )


    with c3:

        with st.container(
            border=True
        ):

            st.caption(
                "MODEL DIFFERENCE"
            )

            st.metric(
                "Risk difference",
                f"{delta_pp:+.1f} pp"
            )


    # ========================================================
    # VISUAL COMPARISON
    # ========================================================

    fig = go.Figure()


    fig.add_trace(

        go.Bar(

            x=[
                "Current Twin",
                "Alternative Twin"
            ],

            y=[
                current_risk * 100,
                alt_risk * 100
            ],

            text=[
                f"{current_risk:.1%}",
                f"{alt_risk:.1%}"
            ],

            textposition="outside",

            hovertemplate=(
                "%{x}<br>"
                "HT risk: %{y:.1f}%"
                "<extra></extra>"
            )
        )
    )


    fig.update_layout(

        title=(
            "Model-Estimated HT Risk"
        ),

        yaxis_title=(
            "Predicted probability (%)"
        ),

        yaxis=dict(
            range=[
                0,
                max(
                    30,
                    current_risk * 120,
                    alt_risk * 120
                )
            ]
        ),

        height=360,

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=40
        ),

        paper_bgcolor=
            "rgba(0,0,0,0)",

        plot_bgcolor=
            "rgba(0,0,0,0)",

    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ========================================================
    # VARIABLE COMPARISON
    # ========================================================

    st.markdown(
        "### What Changed?"
    )


    rows = [

        {
            "Variable":
                "Admission glucose",

            "Current":
                current_glucose,

            "Alternative":
                alt_glucose,

            "Unit":
                "mmol/L"
        },

        {
            "Variable":
                "Systolic BP",

            "Current":
                current_sbp,

            "Alternative":
                alt_sbp,

            "Unit":
                "mmHg"
        },

        {
            "Variable":
                "Onset-to-door",

            "Current":
                current_onset,

            "Alternative":
                alt_onset,

            "Unit":
                "min"
        }
    ]


    if ivt == 1:

        rows.append(
            {
                "Variable":
                    "Door-to-needle",

                "Current":
                    current_dtn,

                "Alternative":
                    alt_dtn,

                "Unit":
                    "min"
            }
        )


    comparison = pd.DataFrame(
        rows
    )


    comparison[
        "Changed"
    ] = (
        comparison["Current"]
        != comparison["Alternative"]
    )


    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # INTERPRETATION
    # ========================================================

    st.markdown(
        "### Model Interpretation"
    )


    if abs(delta_pp) < 0.1:

        st.info(
            "The alternative state produces "
            "almost no change in the model-estimated "
            "HT risk."
        )

    elif delta_pp < 0:

        st.success(
            f"The alternative twin is associated with "
            f"a **{abs(delta_pp):.1f} percentage-point "
            f"lower model-estimated HT risk** than "
            f"the current twin."
        )

    else:

        st.warning(
            f"The alternative twin is associated with "
            f"a **{delta_pp:.1f} percentage-point "
            f"higher model-estimated HT risk** than "
            f"the current twin."
        )


    st.warning(
        "This comparison describes the behaviour of the "
        "prediction model under alternative inputs. "
        "It does not establish that changing these variables "
        "would cause the predicted change in clinical outcome."
    )


    # ========================================================
    # HUMAN-IN-THE-LOOP
    # ========================================================

    st.markdown("---")

    st.markdown(
        "### Clinician Interpretation"
    )

    st.caption(
        "Record whether this scenario is clinically "
        "meaningful or feasible for the current patient."
    )


    clinician_assessment = st.radio(

        "Scenario assessment",

        [
            "Not yet reviewed",
            "Clinically plausible",
            "Plausible with modification",
            "Not clinically plausible",
            "Not relevant to this patient"
        ],

        key="cf_clinician_assessment"
    )


    clinician_note = st.text_area(

        "Clinical comment",

        placeholder=(
            "Optional: explain feasibility, "
            "constraints or clinical context..."
        ),

        key="cf_clinician_note"
    )


    if st.button(
        "Record Scenario Review",
        use_container_width=True
    ):

        st.session_state[
            "counterfactual_clinician_review"
        ] = {

            "assessment":
                clinician_assessment,

            "note":
                clinician_note
        }


        st.success(
            "Clinician scenario review recorded."
        )