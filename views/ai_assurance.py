import streamlit as st
import pandas as pd
import plotly.express as px

from core.monitoring import (
    assess_model_health
)

# ============================================================
# SAFE SESSION STATE
# ============================================================

ASSURANCE_DEFAULTS = {
    "model_version": "M1 HT Risk",
    "model_status": "Ready",
    "selected_site": "Malaysia",
    "adaptation_status": "Not assessed",
    "candidate_strategy": None,
    "candidate_model_status": "Not evaluated",
    "model_approval": "Pending review",
}

for key, value in ASSURANCE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown("# AI Assurance & Adaptation")

st.caption(
    "Monitor model performance, population change "
    "and evidence indicating whether model review "
    "or adaptation may be required."
)


# =========================================================
# MODEL STATUS
# =========================================================

a, b, c, d = st.columns(4)


a.metric(
    "Model",
    st.session_state.get(
        "model_version",
        "M1 HT Risk"
    )
)


b.metric(
    "Current AUC",
    "0.84"
)


c.metric(
    "Population PSI",
    "0.23"
)


d.metric(
    "New labelled cases",
    "524"
)


# =========================================================
# PERFORMANCE TREND
# =========================================================

st.markdown(
    "### Performance Over Time"
)


performance = pd.DataFrame({

    "Period": [
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep"
    ],

    "AUC": [
        .87,
        .86,
        .86,
        .84,
        .82
    ]
})


fig = px.line(

    performance,

    x="Period",

    y="AUC",

    markers=True
)


fig.update_layout(

    paper_bgcolor=
        "rgba(0,0,0,0)",

    plot_bgcolor=
        "rgba(0,0,0,0)"
)


st.plotly_chart(
    fig,
    width="stretch"
)


# =========================================================
# ASSURANCE
# =========================================================

metrics = {

    "auc_drop": 0.05,

    "psi": 0.23,

    "calibration_error":
        0.07,

    "new_labelled_cases":
        524
}


assessment = (
    assess_model_health(
        metrics
    )
)


st.markdown(
    "### Assurance Signals"
)


if assessment[
    "update_needed"
]:

    st.warning(
        "Model review recommended."
    )


    for trigger in assessment[
        "triggers"
    ]:

        st.write(
            "⚠", trigger
        )


else:

    st.success(
        "No model update trigger detected."
    )


# =========================================================
# HUMAN-GOVERNED ADAPTATION
# =========================================================

st.markdown("---")

st.markdown(
    "### Model Adaptation"
)

st.caption(
    "Candidate adaptations are evaluated offline. "
    "The deployed model is never automatically replaced."
)


strategy = st.selectbox(
    "Candidate adaptation strategy",
    [
        "Recalibration",
        "Transfer learning",
        "TrAdaBoost",
        "Local fine-tuning",
        "Full retraining"
    ]
)


if st.button(
    "Evaluate Candidate Adaptation",
    use_container_width=True
):

    st.session_state.candidate_strategy = strategy

    st.session_state.candidate_model_status = (
        "Awaiting offline validation"
    )

    st.info(
        f"{strategy} has been selected as the candidate "
        "adaptation strategy. It must be evaluated offline "
        "against the currently deployed model before any "
        "deployment decision."
    )


# =========================================================
# ADAPTATION STATUS
# =========================================================

if st.session_state.candidate_strategy is not None:

    st.markdown(
        "#### Candidate Adaptation"
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Strategy",
        st.session_state.candidate_strategy
    )

    c2.metric(
        "Status",
        st.session_state.candidate_model_status
    )


# =========================================================
# HUMAN APPROVAL
# =========================================================

st.markdown("---")

st.markdown(
    "### Human Approval"
)

st.caption(
    "Model adaptation requires explicit human review. "
    "No candidate model is automatically promoted "
    "to deployment."
)


approval = st.radio(
    "Candidate model decision",
    [
        "Pending review",
        "Approve for deployment",
        "Reject candidate",
        "Request further validation"
    ]
)


review_note = st.text_area(
    "Reviewer note",
    placeholder=(
        "Optional: record validation concerns, "
        "deployment conditions or reasons for the decision..."
    )
)


if st.button(
    "Record Model Decision",
    use_container_width=True
):

    st.session_state.model_approval = approval

    if approval == "Approve for deployment":

        st.session_state.adaptation_status = (
            "Approved — deployment pending"
        )

    elif approval == "Reject candidate":

        st.session_state.adaptation_status = (
            "Candidate rejected"
        )

    elif approval == "Request further validation":

        st.session_state.adaptation_status = (
            "Further validation required"
        )

    else:

        st.session_state.adaptation_status = (
            "Pending review"
        )


    st.session_state.clinician_feedback = {
        "model_decision": approval,
        "review_note": review_note,
        "strategy": st.session_state.candidate_strategy
    }


    st.success(
        f"Decision recorded: {approval}"
    )