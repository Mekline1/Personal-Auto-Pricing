# Personal Auto Insurance Pricing

An in-progress actuarial pricing project using Python and pandas to analyze claim frequency, recorded claim severity, and recorded loss cost across 678,013 French personal auto liability policies.

## Initial finding

The average recorded claim amount for drivers aged 18–24 was 192% higher than for drivers aged 25–34. After applying the same cap to individual claim amounts in both groups, the difference fell to 14%. The cap was 16,451.22, the 99th percentile of all matched claim amounts. The drop shows how strongly large claims influenced the original comparison. Claim amount records were less complete for some age groups, which limits both comparisons.

## Data and method

The analysis uses the [policy and exposure table](https://www.openml.org/d/41214) and the [claim amount table](https://www.openml.org/d/41215) from OpenML’s freMTPL2 dataset. Claim amounts are summed by policy ID before joining so each policy’s exposure is counted once.

Frequency uses reported claim counts. Severity and loss cost use recorded claim amounts. Across age groups, the number of matched claim amount records ranged from 63% to 85% of reported claim counts, which limits comparisons of severity and loss cost.

## Claim Frequency Model

Drivers aged 18–24 had 1.91 times the observed claim frequency of drivers aged 25–34. After adjusting for vehicle age, region, and bonus-malus score using Poisson regression, the estimated rate ratio was 1.26.

On the 20% of policies held out for testing, mean Poisson deviance fell from 0.3314 for the portfolio-wide baseline to 0.3214 for the model, a 3.0% reduction.

[Download the Excel analysis workbook](personal_auto_pricing_analysis.xlsx)
## Run the analysis

```bash
python -m pip install pandas scikit-learn
python personal_auto_pricing.py
python frequency_model.py
```

The scripts download and cache the data as needed. personal_auto_pricing.py prints the age-group summaries, and frequency_model.py prints the adjusted claim rate ratio and held-out model results.
