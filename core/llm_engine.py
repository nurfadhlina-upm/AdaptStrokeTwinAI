import streamlit as st
from groq import Groq


def get_groq_client():

    api_key = st.secrets.get("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(
        api_key=api_key
    )


def generate_clinical_recommendation(
    patient,
    predictions,
    guideline_context,
    what_if=None,
    clinician_note=None
):

    client = get_groq_client()

    if client is None:
        return (
            "Groq API key is not configured. "
            "Add GROQ_API_KEY to Streamlit secrets."
        )

    prompt = f"""
You are the clinical reasoning and explanation component
of AdaptStroke Twin AI.

The system supports clinicians caring for patients with
acute ischemic stroke.

You MUST distinguish three different information sources:

1. OBSERVED CLINICAL DATA
2. AI MODEL PREDICTIONS
3. AHA/ASA GUIDELINE-GROUNDED CONSIDERATIONS

Never present an AI prediction as an observed clinical fact.

Never claim that a recommendation comes from the guideline
unless it is explicitly contained in the GUIDELINE CONTEXT
provided below.

Do not invent guideline thresholds, contraindications,
drug doses, treatment windows or recommendations.

Do not independently prescribe medication.

Where information is insufficient, explicitly state what
additional information requires clinician assessment.

The final decision belongs to the treating clinical team.


PATIENT DIGITAL TWIN
--------------------
{patient}


AI MODEL OUTPUTS
----------------
{predictions}


GUIDELINE CONTEXT
-----------------
{guideline_context}


WHAT-IF ANALYSIS
----------------
{what_if}


CLINICIAN CONTEXT
-----------------
{clinician_note}


Produce the following sections:

### Clinical Snapshot
Summarise the clinically important current patient state.

### AI Risk Interpretation
Explain relevant AdaptStroke predictions.
Clearly label these as model estimates.

### Guideline-Grounded Considerations
Relate the patient's current state to ONLY the guideline
context supplied above.

For each consideration identify:

- Clinical issue
- Patient-specific evidence
- Guideline-grounded consideration
- Why it may matter

### Monitoring Priorities
Identify parameters or changes that deserve clinician
attention based only on the available patient information
and supplied guideline context.

### What-If Insight
If what-if evidence is available, explain how the simulated
change affected model predictions.

Clearly state that this is a MODEL SIMULATION and does
not demonstrate that changing the variable will cause the
clinical outcome to improve.

### Uncertainty and Missing Information
Identify missing information that limits interpretation.

### Clinician Review
Provide concise questions or considerations for the
clinician.

Do NOT issue a final treatment order.

Finish with:

"AI-supported clinical decision support. Final decisions
require clinician review and consideration of the complete
clinical context."
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content":
                    "You are a guideline-grounded clinical "
                    "decision-support explanation engine."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.15,

        max_tokens=1800
    )

    return response.choices[0].message.content