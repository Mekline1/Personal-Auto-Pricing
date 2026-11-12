import numpy as np
import pandas as pd
from sklearn.linear_model import PoissonRegressor
from sklearn.metrics import mean_poisson_deviance
from sklearn.model_selection import train_test_split

from personal_auto_pricing import load_table


def main():
    policies = load_table("frequency", 20649148, "freMTPL2freq")

    age_band = pd.cut(
        policies["DrivAge"],
        bins=[18, 25, 35, 45, 55, 65, 75, np.inf],
        labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+"],
        right=False,
    )

    # Use ages 25–34 as the reference group.
    features = pd.get_dummies(
        policies[["Region"]].assign(age_band=age_band), dtype=float
    ).drop(columns="age_band_25-34")
    features["vehicle_age_decades"] = policies["VehAge"] / 10
    features["bonus_malus_per_10"] = policies["BonusMalus"] / 10

    train, test = train_test_split(
        policies.index, test_size=0.2, random_state=42
    )

    exposure = policies["Exposure"]
    claims = policies["ClaimNb"]
    claim_rate = claims / exposure

    # Fit annual claim rates, giving each policy weight equal to its insured years.
    model = PoissonRegressor(alpha=0, max_iter=1000, tol=1e-8)
    model.fit(
        features.loc[train],
        claim_rate.loc[train],
        sample_weight=exposure.loc[train],
    )

    # Convert annual rates to expected claim counts for each test policy.
    baseline_rate = claims.loc[train].sum() / exposure.loc[train].sum()
    baseline_counts = baseline_rate * exposure.loc[test]
    predicted_counts = model.predict(features.loc[test]) * exposure.loc[test]

    age_coefficient = model.coef_[features.columns.get_loc("age_band_18-24")]
    adjusted_ratio = np.exp(age_coefficient)
    baseline_deviance = mean_poisson_deviance(claims.loc[test], baseline_counts)
    model_deviance = mean_poisson_deviance(claims.loc[test], predicted_counts)
    improvement = 100 * (baseline_deviance - model_deviance) / baseline_deviance

    print(f"Adjusted claim rate ratio, ages 18–24 vs. 25–34: {adjusted_ratio:.2f}x")
    print(f"Held-out mean Poisson deviance, baseline: {baseline_deviance:.4f}")
    print(f"Held-out mean Poisson deviance, model:    {model_deviance:.4f}")
    print(f"Reduction in mean Poisson deviance: {improvement:.1f}%")


if __name__ == "__main__":
    main()