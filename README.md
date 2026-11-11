# Personal Auto Insurance Pricing

An in-progress actuarial pricing project using Python and pandas to analyze claim frequency, recorded claim severity, and recorded loss cost across 678,013 French personal auto liability policies.

## Initial finding

The average recorded claim amount for drivers aged 18–24 was 192% higher than for drivers aged 25–34. After capping claim amounts at the same 99th-percentile threshold (16,451.22) across all age groups, the gap fell to 14%. This shows how much large claims influenced the original comparison. Claim amount records were less complete for some age groups, which still limits the comparison.

## Data and method

The analysis uses the [policy and exposure table](https://www.openml.org/d/41214) and the [claim amount table](https://www.openml.org/d/41215) from OpenML’s freMTPL2 dataset. Claim amounts are summed by policy ID before joining so each policy’s exposure is counted once.

Frequency uses reported claim counts. Severity and loss cost use recorded claim amounts. Across age groups, the number of matched claim amount records ranged from 63% to 85% of reported claim counts, which limits comparisons of severity and loss cost.

## Run the analysis

```bash
python -m pip install pandas
python personal_auto_pricing.py
```

The script downloads the data on the first run and prints the results by driver age group. On Windows, use `py` in place of `python` if that’s how you launch Python.
