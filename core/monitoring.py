def assess_model_health(metrics):
    """
    Prototype governance rules.

    Thresholds must later be configured
    from the validated governance protocol.
    """

    triggers = []


    if metrics["auc_drop"] >= 0.05:

        triggers.append(
            "Performance deterioration"
        )


    if metrics["psi"] >= 0.20:

        triggers.append(
            "Population drift"
        )


    if (
        metrics["calibration_error"]
        >= 0.10
    ):

        triggers.append(
            "Calibration deterioration"
        )


    if (
        metrics["new_labelled_cases"]
        >= 500
    ):

        triggers.append(
            "Sufficient new labelled evidence"
        )


    update_needed = (
        len(triggers) > 0
    )


    return {

        "update_needed":
            update_needed,

        "triggers":
            triggers
    }