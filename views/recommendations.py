import streamlit as st

from core.twin_engine import build_twin_predictions
from core.guideline_engine import build_guideline_context
from core.llm_engine import generate_clinical_recommendation


st.title("Clinical Recommendations")

st.caption(
    "Guideline-grounded, AI-supported clinical reasoning "
    "for the active patient digital twin."
)


patient = st.session_state.get("patient")

if patient is None:

    st.info(
        "Create or load a Patient Digital Twin first."
    )

    st.stop()


# ============================================================
# MODEL INTELLIGENCE
# ============================================================

predictions = build_twin_predictions(
    patient
)


guideline_context = build_guideline_context(
    patient,
    predictions
)


# ============================================================
# PATIENT STATE
# ============================================================

st.markdown("## Current Twin State")


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Twin ID",
    st.session_state.get(
        "patient_id",
        "—"
    )
)


ht_risk = (
    predictions
    .get("treatment", {})
    .get("ht_probability")
)


c2.metric(
    "Predicted HT Risk",
    (
        f"{ht_risk:.1%}"
        if ht_risk is not None
        else "—"
    )
)


c3.metric(
    "NIHSS",
    patient.get(
        "baseline_nihss",
        "—"
    )
)


c4.metric(
    "Current Stage",
    st.session_state.get(
        "twin_stage",
        "Treatment"
    )
)


# ============================================================
# GUIDELINE CONTEXT
# ============================================================

st.markdown("## Guideline Intelligence")

st.caption(
    "Patient-specific considerations derived from the "
    "2026 AHA/ASA acute ischemic stroke guideline."
)


for item in guideline_context:

    with st.container(border=True):

        st.markdown(
            f"**{item['domain']}**"
        )

        st.write(
            item["patient_value"]
        )

        st.caption(
            item["guideline_context"]
        )


# ============================================================
# LLM
# ============================================================

st.markdown("## AI-Supported Clinical Reasoning")

st.caption(
    "Groq synthesises the patient twin, predictive models "
    "and retrieved guideline context. The generated output "
    "requires clinician review."
)


clinician_context = st.text_area(
    "Additional clinical context",
    placeholder=(
        "Optional: add clinical observations, constraints, "
        "treatment considerations or questions..."
    )
)


if st.button(
    "Generate Clinical Recommendation",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Synthesising patient, model and guideline evidence..."
    ):

        recommendation = (
            generate_clinical_recommendation(

                patient=patient,

                predictions=predictions,

                guideline_context=guideline_context,

                what_if=st.session_state.get(
                    "what_if_result"
                ),

                clinician_note=clinician_context
            )
        )


    st.session_state[
        "current_recommendation"
    ] = recommendation


# ============================================================
# DISPLAY
# ============================================================

recommendation = st.session_state.get(
    "current_recommendation"
)


if recommendation:

    st.markdown("### Recommendation")

    with st.container(border=True):

        st.markdown(
            recommendation
        )


    # ========================================================
    # HUMAN IN THE LOOP
    # ========================================================

    st.markdown("## Clinician Review")

    st.caption(
        "AI-generated recommendations are provisional "
        "until reviewed by the clinician."
    )


    review = st.radio(

        "Clinical assessment",

        [
            "Pending review",
            "Accept",
            "Modify",
            "Reject"
        ],

        horizontal=True
    )


    modification = None


    if review == "Modify":

        modification = st.text_area(
            "Clinician modification",
            placeholder=(
                "Document the modified recommendation "
                "and clinical rationale."
            )
        )


    rationale = st.text_area(
        "Clinical rationale / comment",
        placeholder=(
            "Optional clinician reasoning, disagreement "
            "or additional context."
        )
    )


    if st.button(
        "Record Clinician Decision",
        use_container_width=True
    ):

        decision = {

            "ai_recommendation":
                recommendation,

            "decision":
                review,

            "modification":
                modification,

            "clinician_rationale":
                rationale,

            "twin_stage":
                st.session_state.get(
                    "twin_stage"
                )
        }


        if (
            "recommendation_history"
            not in st.session_state
        ):

            st.session_state[
                "recommendation_history"
            ] = []


        st.session_state[
            "recommendation_history"
        ].append(
            decision
        )


        st.success(
            "Clinician decision recorded in the "
            "patient twin."
        )