from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "stroke_models"
DATA_FILE = (
    BASE_DIR
    / "synthetic_data"
    / "synthetic_asean_stroke_v2.csv"
)


# ============================================================
# MODEL FILES
# ============================================================

MODEL_FILES = {
    "ht": "M1_HT_Risk.joblib",
    "early_mrs": "M2_Early_Discharge_mRS.joblib",
    "updated_mrs": "M3_Updated_Discharge_mRS.joblib",
    "mrs_90d": "M4_90Day_mRS.joblib",
    "mortality_90d": "M5_90Day_Mortality.joblib",
}


# ============================================================
# LOADERS
# ============================================================

@st.cache_resource
def load_model(model_key):

    if model_key not in MODEL_FILES:
        raise ValueError(
            f"Unknown model key: {model_key}"
        )

    path = MODEL_DIR / MODEL_FILES[model_key]

    if not path.exists():
        return None

    return joblib.load(path)


@st.cache_data
def load_reference_data():

    if not DATA_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(
        DATA_FILE,
        low_memory=False
    )


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model_info(model_key):

    model = load_model(model_key)

    if model is None:
        return None

    return {
        "algorithm": model.get(
            "algorithm",
            "Unknown"
        ),
        "features": model.get(
            "features",
            []
        ),
        "target": model.get(
            "target",
            "Unknown"
        ),
        "metrics": model.get(
            "metrics",
            {}
        ),
        "model_type": model.get(
            "model_type",
            "Unknown"
        ),
        "prediction_time": model.get(
            "prediction_time",
            model_key
        )
    }


# ============================================================
# INPUT PREPARATION
# ============================================================

def patient_to_series(patient):

    if isinstance(patient, pd.Series):
        return patient.copy()

    if isinstance(patient, dict):
        return pd.Series(patient)

    if isinstance(patient, pd.DataFrame):

        if patient.empty:
            raise ValueError(
                "Patient DataFrame is empty."
            )

        return patient.iloc[0].copy()

    raise TypeError(
        "Patient must be a dict, pandas Series "
        "or one-row DataFrame."
    )


def prepare_patient_for_model(
    patient,
    model_object
):

    patient = patient_to_series(patient)

    features = model_object.get(
        "features",
        []
    )

    values = {}

    for feature in features:

        if feature in patient.index:
            values[feature] = [
                patient[feature]
            ]

        else:
            values[feature] = [
                np.nan
            ]

    return pd.DataFrame(values)


# ============================================================
# BINARY PREDICTION
# ============================================================

def predict_binary(
    patient,
    model_key
):

    model = load_model(model_key)

    if model is None:
        return None

    X = prepare_patient_for_model(
        patient,
        model
    )

    pipeline = model["pipeline"]

    probability = (
        pipeline
        .predict_proba(X)[0, 1]
    )

    return float(probability)


# ============================================================
# mRS PREDICTION
# ============================================================

def predict_mrs(
    patient,
    model_key
):

    model = load_model(model_key)

    if model is None:
        return None

    X = prepare_patient_for_model(
        patient,
        model
    )

    prediction = (
        model["pipeline"]
        .predict(X)[0]
    )

    return int(prediction)


# ============================================================
# ALL PREDICTIONS
# ============================================================

def predict_patient_state(patient):

    return {

        "ht_probability":
            predict_binary(
                patient,
                "ht"
            ),

        "early_discharge_mrs":
            predict_mrs(
                patient,
                "early_mrs"
            ),

        "updated_discharge_mrs":
            predict_mrs(
                patient,
                "updated_mrs"
            ),

        "mrs_90d":
            predict_mrs(
                patient,
                "mrs_90d"
            ),

        "mortality_90d":
            predict_binary(
                patient,
                "mortality_90d"
            )
    }


# ============================================================
# DISPLAY RISK LABEL
#
# Prototype visualisation only.
# These are NOT clinically validated thresholds.
# ============================================================

def risk_label(probability):

    if probability is None:
        return "Unavailable"

    if probability < 0.10:
        return "Lower model-estimated risk"

    if probability < 0.20:
        return "Intermediate model-estimated risk"

    return "Higher model-estimated risk"


# ============================================================
# LOCAL MODEL SENSITIVITY
#
# Preserves the logic from the original AdaptStroke dashboard.
#
# This is NOT SHAP.
# This is NOT causal inference.
# ============================================================

def local_sensitivity(
    patient,
    model_key="ht",
    max_features=8
):

    model = load_model(model_key)

    reference_df = load_reference_data()

    if model is None or reference_df.empty:
        return pd.DataFrame()

    patient = patient_to_series(patient)

    baseline = predict_binary(
        patient,
        model_key
    )

    results = []

    features = model.get(
        "features",
        []
    )

    for feature in features:

        if feature not in patient.index:
            continue

        if feature not in reference_df.columns:
            continue

        original = patient[feature]

        column = reference_df[feature]

        modified = patient.copy()

        if pd.api.types.is_numeric_dtype(
            column
        ):

            reference_value = (
                column
                .dropna()
                .median()
            )

        else:

            mode = (
                column
                .dropna()
                .mode()
            )

            if len(mode) == 0:
                continue

            reference_value = mode.iloc[0]

        if pd.isna(reference_value):
            continue

        modified[feature] = reference_value

        try:

            alternative = predict_binary(
                modified,
                model_key
            )

        except Exception:
            continue

        contribution = (
            baseline
            - alternative
        )

        results.append(
            {
                "Feature": feature,
                "Patient value": original,
                "Reference value":
                    reference_value,
                "Local contribution":
                    contribution,
                "Absolute contribution":
                    abs(contribution)
            }
        )

    if not results:
        return pd.DataFrame()

    result = pd.DataFrame(results)

    return (
        result
        .sort_values(
            "Absolute contribution",
            ascending=False
        )
        .head(max_features)
        .reset_index(drop=True)
    )


# ============================================================
# WHAT-IF PREDICTION
# ============================================================

def predict_ht_scenario(
    patient,
    changes
):

    scenario = patient_to_series(
        patient
    )

    for feature, value in changes.items():

        scenario[feature] = value

    probability = predict_binary(
        scenario,
        "ht"
    )

    return probability, scenario