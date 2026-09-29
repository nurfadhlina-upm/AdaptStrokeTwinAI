import streamlit as st


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="AdaptStroke Twin AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# STYLE
# =========================================================

with open(
    "assets/style.css",
    encoding="utf-8"
) as f:

    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# =========================================================
# GLOBAL DIGITAL TWIN STATE
# =========================================================

DEFAULTS = {

    # Longitudinal twin
    "twin_stage": "Admission",
    "twin_stage_index": 0,
    "twin_history": [],

    # HT prediction
    "ht_probability": None,
    "ht_risk_label": None,
    "ht_explanation": None,
    "ht_prediction_stage": None,
    "ht_prediction_patient": None,

    # Other model predictions
    "predictions": None,

    # What-if
    "counterfactual_result": None,
    "counterfactual_clinician_review": None,

    # Clinical intelligence / LLM
    "current_recommendation": None,
    "recommendation_history": [],
    "latest_clinical_note": "",

    # Model management
    "model_version": "M1 HT Risk",
    "model_status": "Ready",
    "selected_site": "Malaysia",
    "adaptation_status": "Not assessed",

    # HITL
    "clinician_feedback": None,

}


for key, value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# HEADER
# =========================================================

header_html = """
<div class="twin-header">
<div class="brand">
ADAPTSTROKE <span class="brand-highlight">TWIN AI</span>
</div>
<div class="subtitle">
Adaptive Digital Twin for Stroke Decision Support
</div>
</div>
"""

st.markdown(
    header_html,
    unsafe_allow_html=True
)


# =========================================================
# NAVIGATION
# =========================================================

pages = {

    "Clinical Workspace": [

        st.Page(
            "views/twin_overview.py",
            title="Twin Overview",
            icon=":material/home:",
            default=True
        ),

        st.Page(
            "views/patient_twin.py",
            title="Patient Digital Twin",
            icon=":material/person:"
        ),

        st.Page(
            "views/ht_risk.py",
            title="HT Risk & Explanation",
            icon=":material/neurology:"
        ),

        st.Page(
            "views/update_state.py",
            title="Patient Journey",
            icon=":material/timeline:"
        ),

        st.Page(
            "views/what_if.py",
            title="What-If Explorer",
            icon=":material/compare_arrows:"
        ),

        st.Page(
            "views/recommendations.py",
            title="Clinical Recommendations",
            icon=":material/clinical_notes:"
        ),

        st.Page(
            "views/copilot.py",
            title="Clinical Intelligence",
            icon=":material/psychology:"
        ),
    ],


    "AI Management": [

        st.Page(
            "views/ai_assurance.py",
            title="AI Assurance & Adaptation",
            icon=":material/monitoring:"
        )

    ]
}


page = st.navigation(pages)

page.run()