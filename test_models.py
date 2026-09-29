from core.model_engine import (
    load_model,
    get_model_info,
    load_reference_data
)


print("\nADAPTSTROKE MODEL CHECK")
print("=" * 60)


data = load_reference_data()

print(
    f"Reference patients: {len(data)}"
)


model_keys = [
    "ht",
    "early_mrs",
    "updated_mrs",
    "mrs_90d",
    "mortality_90d"
]


for key in model_keys:

    print()
    print("-" * 60)
    print(key.upper())

    model = load_model(key)

    if model is None:

        print("MODEL NOT FOUND")

        continue

    info = get_model_info(key)

    print("Status: OK")
    print(
        "Algorithm:",
        info["algorithm"]
    )

    print(
        "Target:",
        info["target"]
    )

    print(
        "Number of features:",
        len(info["features"])
    )

    print(
        "Features:"
    )

    for feature in info["features"]:
        print(
            "  -",
            feature
        )