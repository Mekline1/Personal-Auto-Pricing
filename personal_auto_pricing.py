"""Run with Python and pandas. OpenML freMTPL2 tables are cached locally."""
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

DATA = Path("freMTPL2")


def load_table(name, file_id, dataset):
    DATA.mkdir(exist_ok=True)
    path = DATA / f"{name}.arff"
    if not path.exists():
        temporary = path.with_suffix(".tmp")
        urlretrieve(f"https://openml.org/data/v1/download/{file_id}/{dataset}.arff", temporary)
        temporary.replace(path)
    with path.open() as source:
        columns = []
        for line in source:
            if line.lower().startswith("@attribute"):
                columns.append(line.split()[1].strip("'"))
            if line.strip().lower() == "@data":
                return pd.read_csv(source, names=columns, na_values="?")
    raise ValueError(f"No data section in {path}")


def main():
    policies = load_table("frequency", 20649148, "freMTPL2freq")
    claims = load_table("severity", 20649149, "freMTPL2sev")
    assert policies.IDpol.is_unique and policies.Exposure.gt(0).all()
    assert claims.ClaimAmount.notna().all()
    matched = claims[claims.IDpol.isin(policies.IDpol)].copy()
    cap = matched["ClaimAmount"].quantile(0.99)
    matched["CappedClaimAmount"] = matched["ClaimAmount"].clip(upper=cap)
    totals = matched.groupby("IDpol").ClaimAmount.agg(
        matched_claims="size", recorded_losses="sum"
    )
    portfolio = policies.join(totals, on="IDpol", validate="one_to_one")
    columns = ["matched_claims", "recorded_losses"]
    portfolio[columns] = portfolio[columns].fillna(0)
    assert len(portfolio) == len(policies)
    assert portfolio.matched_claims.sum() == len(matched)
    portfolio["age"] = pd.cut(
        portfolio.DrivAge, [18, 25, 35, 45, 55, 65, 75, float("inf")],
        right=False, labels=["18–24", "25–34", "35–44", "45–54", "55–64", "65–74", "75+"],
    )
    assert portfolio.age.notna().all()
    summary = portfolio.groupby("age", observed=True).agg(
        policies=("IDpol", "size"), exposure=("Exposure", "sum"),
        reported_claims=("ClaimNb", "sum"), matched_claims=("matched_claims", "sum"),
        recorded_losses=("recorded_losses", "sum"),
    )
    summary["claims_per_100_years"] = 100 * summary.reported_claims / summary.exposure
    summary["average_recorded_severity"] = summary.recorded_losses / summary.matched_claims
    summary["recorded_loss_per_year"] = summary.recorded_losses / summary.exposure
    # Aggregate count ratio is a diagnostic, since some policies have excess records.
    summary["matched_to_reported_pct"] = 100 * summary.matched_claims / summary.reported_claims
    print(f"Unmatched claim amount rows: {len(claims) - len(matched):,}")
    print(portfolio.matched_claims.sub(portfolio.ClaimNb).pipe(
        lambda difference: {"fewer": int(difference.lt(0).sum()), "more": int(difference.gt(0).sum())}
    ))    
    capped_by_policy = matched.groupby("IDpol")["CappedClaimAmount"].sum()
    portfolio["capped_losses"] = portfolio["IDpol"].map(capped_by_policy).fillna(0)
    capped_by_age = portfolio.groupby("age", observed=True)["capped_losses"].sum()

    summary["capped_average_severity"] = capped_by_age / summary["matched_claims"]
    frequency_table = summary.rename(columns={
        "policies": "Policies",
        "claims_per_100_years": "Claims per 100 insured years",
        "matched_to_reported_pct": "Claim amounts matched (%)",
    })[["Policies", "Claims per 100 insured years", "Claim amounts matched (%)"]]

    severity_table = summary.rename(columns={
        "average_recorded_severity": "Original average",
        "capped_average_severity": "Capped average",
        "recorded_loss_per_year": "Uncapped recorded loss per insured year",
    })[["Original average", "Capped average", "Uncapped recorded loss per insured year"]]

    print("\nREPORTED CLAIM FREQUENCY BY DRIVER AGE")
    print(frequency_table.rename_axis("Driver age").to_string(formatters={
        "Policies": "{:,.0f}".format,
        "Claims per 100 insured years": "{:,.2f}".format,
        "Claim amounts matched (%)": "{:.1f}".format,
    }))

    print(f"\nRECORDED CLAIM SEVERITY BY DRIVER AGE (cap: {cap:,.2f})")
    print(severity_table.rename_axis("Driver age").to_string(
        float_format="{:,.2f}".format
    ))


if __name__ == "__main__":
    main()
