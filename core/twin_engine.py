from core.model_engine import (
    predict_binary,
    predict_mrs
)


def has_fields(patient, fields):
    return all(
        field in patient
        and patient.get(field) is not None
        for field in fields
    )


def build_twin_predictions(patient):

    results = {

        "admission": {
            "early_discharge_mrs": None
        },

        "treatment": {
            "ht_probability": None
        },

        "hospital": {
            "updated_discharge_mrs": None
        },

        "follow_up": {
            "mrs_90d": None,
            "mortality_90d": None
        }
    }


    # ========================================================
    # 1. ADMISSION
    # ========================================================

    try:

        results["admission"][
            "early_discharge_mrs"
        ] = predict_mrs(
            patient,
            "early_mrs"
        )

    except Exception:
        pass


    # ========================================================
    # 2. TREATMENT
    # ========================================================

    treatment_fields = [
        "iv_thrombolysis",
        "mechanical_thrombectomy"
    ]


    if has_fields(
        patient,
        treatment_fields
    ):

        try:

            results["treatment"][
                "ht_probability"
            ] = predict_binary(
                patient,
                "ht"
            )

        except Exception:
            pass


    # ========================================================
    # 3. HOSPITAL COURSE
    # ========================================================

    hospital_fields = [
        "hemorrhagic_transformation",
        "symptomatic_ich",
        "recanalization_status"
    ]


    hospital_ready = has_fields(
        patient,
        hospital_fields
    )


    if hospital_ready:

        try:

            results["hospital"][
                "updated_discharge_mrs"
            ] = predict_mrs(
                patient,
                "updated_mrs"
            )

        except Exception:
            pass


    # ========================================================
    # 4. FOLLOW-UP OUTLOOK
    #
    # M4/M5 use later clinical information.
    # Do not expose them as though they were admission models.
    # ========================================================

    discharge_ready = (
        hospital_ready
        and has_fields(
            patient,
            ["discharge_mrs"]
        )
    )


    if discharge_ready:

        try:

            results["follow_up"][
                "mrs_90d"
            ] = predict_mrs(
                patient,
                "mrs_90d"
            )

        except Exception:
            pass


        try:

            results["follow_up"][
                "mortality_90d"
            ] = predict_binary(
                patient,
                "mortality_90d"
            )

        except Exception:
            pass


    return results