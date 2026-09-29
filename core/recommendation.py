def build_recommendation_context(
    patient,
    ht_probability,
    explanations=None,
    counterfactual=None
):

    return {

        "patient": patient,

        "ht_probability":
            ht_probability,

        "explanations":
            explanations or [],

        "counterfactual":
            counterfactual,

        "required_output": {

            "risk_summary":
                "Concise interpretation",

            "key_factors":
                [],

            "clinical_considerations":
                [],

            "monitoring_considerations":
                [],

            "what_if_interpretation":
                "",

            "uncertainty":
                "",

            "requires_clinician_review":
                True
        }
    }