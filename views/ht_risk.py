import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.model_engine import (
    predict_binary,
    local_sensitivity,
    get_model_info,
    risk_label
)


# ============================================================
# PAGE
# ============================================================

st.title("HT Risk & Explanation")

st.caption(
    "Estimate hemorrhagic transformation risk using the "
    "current patient state and explore factors influencing "
    "the model prediction."
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
# DIGITAL TWIN STAGE
# ============================================================

stage = st.session_state.get(
    "twin_stage",
    "Admission"
)

stage_index = st.session_state.get(
    "twin_stage_index",
    0
)

st.markdown("### Digital Twin Context")

c1, c2 = st.columns(2)

c1.metric(
    "Current Stage",
    stage
)

c2.metric(
    "Patient",
    st.session_state.get("patient_id") or "—"
)


# HT prediction requires treatment information
if stage == "Admission":

    st.info(
        "HT risk assessment is not yet available at the "
        "Admission stage. Advance the patient digital twin "
        "to Treatment so that treatment information can be "
        "incorporated into the prediction."
    )

    st.markdown(
        "#### Why is the assessment unavailable?"
    )

    st.write(
        "The HT model is designed to estimate hemorrhagic "
        "transformation risk after the treatment state is "
        "known. Treatment variables are intentionally hidden "
        "during Admission to prevent future information from "
        "leaking into the prediction."
    )

    st.stop()

# ============================================================
# MODEL INFORMATION
# ============================================================

model_info = get_model_info("ht")

if model_info is None:

    st.error(
        "The HT prediction model could not be loaded."
    )

    st.stop()


# ============================================================
# PATIENT CONTEXT
# ============================================================

st.markdown("### Current Patient State")

c1, c2, c3, c4 = st.columns(4)


def patient_value(name, default="—"):

    if hasattr(patient, "get"):
        return patient.get(name, default)

    return default


c1.metric(
    "Patient",
    st.session_state.get("patient_id") or "—"
)

c2.metric(
    "NIHSS",
    patient_value("baseline_nihss")
)

c3.metric(
    "ASPECTS",
    patient_value("aspects")
)

c4.metric(
    "Systolic BP",
    patient_value("systolic_bp")
)


# ============================================================
# TREATMENT CONTEXT
# ============================================================

with st.expander(
    "Treatment information used for HT assessment",
    expanded=True
):

    a, b, c = st.columns(3)

    ivt = patient_value(
        "iv_thrombolysis",
        None
    )

    mt = patient_value(
        "mechanical_thrombectomy",
        None
    )

    dtn = patient_value(
        "door_to_needle_min",
        None
    )


    # IV thrombolysis
    if ivt == 1:
        ivt_display = "Yes"
    elif ivt == 0:
        ivt_display = "No"
    else:
        ivt_display = "Not available"


    # Mechanical thrombectomy
    if mt == 1:
        mt_display = "Yes"
    elif mt == 0:
        mt_display = "No"
    else:
        mt_display = "Not available"


    # Door-to-needle
    if ivt == 1 and dtn is not None:
        dtn_display = f"{dtn} min"
    elif ivt == 0:
        dtn_display = "N/A"
    else:
        dtn_display = "Not available"


    a.metric(
        "IV thrombolysis",
        ivt_display
    )

    b.metric(
        "Door-to-needle",
        dtn_display
    )

    c.metric(
        "Mechanical thrombectomy",
        mt_display
    )


# ============================================================
# RUN REAL M1 MODEL
# ============================================================

st.markdown("### HT Risk Assessment")


# Prediction is only generated prospectively
# during the Treatment stage.
if stage == "Treatment":

    run_prediction = st.button(
        "Assess HT Risk",
        type="primary",
        use_container_width=True
    )

else:

    run_prediction = False

    if st.session_state.get(
        "ht_probability"
    ) is None:

        st.warning(
            "No prospective HT prediction was recorded "
            "during the Treatment stage."
        )


# Run M1 only when requested at Treatment stage
if run_prediction:

    try:

        probability = predict_binary(
            patient,
            "ht"
        )

        st.session_state.ht_probability = (
            probability
        )

        st.session_state.ht_risk_label = (
            risk_label(probability)
        )

        # Record when and for whom prediction was made
        st.session_state.ht_prediction_stage = (
            stage
        )

        st.session_state.ht_prediction_patient = (
            st.session_state.get(
                "patient_id"
            )
        )

        st.success(
            "HT risk assessment completed."
        )

    except Exception as error:

        st.error(
            "The HT model could not complete "
            "the prediction."
        )

        st.exception(error)

# ============================================================
# RESULTS
# ============================================================

prob = st.session_state.get(
    "ht_probability"
)


if prob is not None:

    st.markdown("---")

    left, right = st.columns(
        [0.85, 1.15]
    )


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    with left:

        st.markdown(
            "### Model Estimate"
        )

        st.metric(
            "Predicted HT probability",
            f"{prob:.1%}"
        )

        label = risk_label(prob)

        if prob >= 0.20:

            st.warning(label)

        elif prob >= 0.10:

            st.info(label)

        else:

            st.success(label)


        st.caption(
            "The displayed category is for interface "
            "interpretation only. Clinical thresholds "
            "must be defined and validated separately."
        )


        st.markdown(
            "#### Model"
        )

        st.write(
            f"**Algorithm:** "
            f"{model_info['algorithm']}"
        )

        st.write(
            f"**Prediction stage:** "
            f"Treatment-time HT assessment"
        )


    # --------------------------------------------------------
    # GAUGE
    # --------------------------------------------------------

    with right:

        fig = go.Figure(

            go.Indicator(

                mode="gauge+number",

                value=prob * 100,

                number={
                    "suffix": "%",
                    "font": {
                        "size": 42
                    }
                },

                title={
                    "text":
                    "Model-estimated HT probability"
                },

                gauge={

                    "axis": {
                        "range": [0, 100]
                    },

                    "bar": {
                        "thickness": 0.35
                    }
                }
            )
        )


        fig.update_layout(

            height=300,

            margin=dict(
                l=30,
                r=30,
                t=50,
                b=20
            ),

            paper_bgcolor=
                "rgba(0,0,0,0)",

        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ============================================================
    # PREDICTED VS OBSERVED OUTCOME
    # ============================================================

    if stage in [
        "Hospital Course",
        "Discharge & Follow-Up"
    ]:

        st.markdown("---")

        st.markdown(
            "### Prediction–Outcome Comparison"
        )

        observed_ht = patient_value(
            "hemorrhagic_transformation",
            None
        )

        left_obs, right_obs = st.columns(2)

        # Prospective prediction
        with left_obs:

            st.markdown(
                "#### AI Prediction"
            )

            st.metric(
                "Treatment-stage predicted HT risk",
                f"{prob:.1%}"
            )

            st.caption(
                "Prediction generated before the "
                "hospital-course outcome became available."
            )

        # Observed outcome
        with right_obs:

            st.markdown(
                "#### Observed Clinical Outcome"
            )

            if observed_ht == 1:

                st.metric(
                    "Hemorrhagic Transformation",
                    "Observed"
                )

            elif observed_ht == 0:

                st.metric(
                    "Hemorrhagic Transformation",
                    "Not observed"
                )

            else:

                st.metric(
                    "Hemorrhagic Transformation",
                    "Unavailable"
                )

        st.info(
            "This comparison is for longitudinal model "
            "evaluation. A probability estimate should not "
            "be interpreted as a deterministic prediction "
            "of an individual patient's outcome."
        )

    # ========================================================
    # LOCAL EXPLANATION
    # ========================================================

    st.markdown("---")

    st.markdown(
        "### Why did the model produce this estimate?"
    )

    st.caption(
        "The explanation below evaluates how the "
        "prediction changes when individual patient "
        "variables are replaced by reference values "
        "from the synthetic cohort."
    )


    try:

        explanation = local_sensitivity(
            patient,
            model_key="ht",
            max_features=8
        )

    except Exception as error:

        explanation = pd.DataFrame()

        st.warning(
            "Local sensitivity analysis could "
            "not be calculated."
        )

        st.exception(error)


    if explanation.empty:

        st.info(
            "No local sensitivity results "
            "are available for this patient."
        )

    else:

        # Save for recommendation / LLM later

        st.session_state[
            "ht_explanation"
        ] = explanation


        # ----------------------------------------------------
        # FRIENDLY FEATURE NAMES
        # ----------------------------------------------------

        friendly_names = {

            "age":
                "Age",

            "baseline_nihss":
                "Baseline NIHSS",

            "aspects":
                "ASPECTS",

            "systolic_bp":
                "Systolic blood pressure",

            "diastolic_bp":
                "Diastolic blood pressure",

            "admission_glucose_mmol_l":
                "Admission glucose",

            "hba1c":
                "HbA1c",

            "platelets_10e9_l":
                "Platelets",

            "inr":
                "INR",

            "creatinine_umol_l":
                "Creatinine",

            "onset_to_door_min":
                "Onset-to-door time",

            "door_to_needle_min":
                "Door-to-needle time",

            "iv_thrombolysis":
                "IV thrombolysis",

            "mechanical_thrombectomy":
                "Mechanical thrombectomy",

            "large_vessel_occlusion":
                "Large vessel occlusion",

            "prestroke_mrs":
                "Pre-stroke mRS"
        }


        chart_df = explanation.copy()

        chart_df[
            "Display feature"
        ] = chart_df[
            "Feature"
        ].map(
            friendly_names
        ).fillna(
            chart_df["Feature"]
        )


        chart_df[
            "Effect (percentage points)"
        ] = (
            chart_df[
                "Local contribution"
            ]
            * 100
        )


        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        chart_df = (
            chart_df
            .sort_values(
                "Absolute contribution",
                ascending=True
            )
        )


        fig2 = go.Figure()


        fig2.add_trace(

            go.Bar(

                x=chart_df[
                    "Effect (percentage points)"
                ],

                y=chart_df[
                    "Display feature"
                ],

                orientation="h",

                hovertemplate=(
                    "%{y}<br>"
                    "Local prediction difference: "
                    "%{x:.2f} percentage points"
                    "<extra></extra>"
                )
            )
        )


        fig2.add_vline(
            x=0,
            line_width=1
        )


        fig2.update_layout(

            title=(
                "Largest local influences "
                "on this prediction"
            ),

            xaxis_title=(
                "Change in predicted HT risk "
                "relative to reference value "
                "(percentage points)"
            ),

            yaxis_title="",

            height=420,

            margin=dict(
                l=20,
                r=20,
                t=60,
                b=50
            ),

            paper_bgcolor=
                "rgba(0,0,0,0)",

            plot_bgcolor=
                "rgba(0,0,0,0)",

        )


        st.plotly_chart(
            fig2,
            use_container_width=True
        )


        # ----------------------------------------------------
        # TOP FACTORS
        # ----------------------------------------------------

        st.markdown(
            "#### Patient-specific model influences"
        )


        display_df = (
            explanation[
                [
                    "Feature",
                    "Patient value",
                    "Reference value",
                    "Local contribution"
                ]
            ]
            .copy()
        )


        display_df[
            "Feature"
        ] = (
            display_df["Feature"]
            .map(friendly_names)
            .fillna(
                display_df["Feature"]
            )
        )


        display_df[
            "Prediction difference"
        ] = (
            display_df[
                "Local contribution"
            ]
            * 100
        ).round(2)


        display_df = display_df.drop(
            columns=[
                "Local contribution"
            ]
        )


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


        st.info(
            "These values represent local model "
            "sensitivity, not causal effects. "
            "A positive difference means that replacing "
            "the patient's value with the cohort reference "
            "value lowered the model-estimated risk; "
            "a negative difference means the opposite."
        )


    # ========================================================
    # NEXT STEP
    # ========================================================

    st.markdown("---")

    st.markdown(
        "### Continue the Patient Twin"
    )

    st.write(
        "The current HT estimate and local explanation "
        "are now stored in the patient twin. Continue to "
        "**What-If Explorer** to examine alternative "
        "patient states."
    )