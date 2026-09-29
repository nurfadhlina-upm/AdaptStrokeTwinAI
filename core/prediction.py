def predict_ht(patient):
    """
    Temporary prototype.

    Replace this function with the trained
    HT model from the existing project.
    """

    score = 0.08

    score += (
        patient["nihss"] / 42
    ) * 0.30

    score += (
        max(
            patient["glucose"] - 100,
            0
        ) / 400
    ) * 0.20

    score += (
        max(
            patient["systolic_bp"] - 120,
            0
        ) / 200
    ) * 0.15

    score += (
        patient["age"] / 100
    ) * 0.10


    if patient["thrombolysis"]:

        score += 0.05


    probability = min(
        max(score, 0.01),
        0.95
    )


    return {
        "probability": probability,
        "prediction":
            int(probability >= 0.5)
    }