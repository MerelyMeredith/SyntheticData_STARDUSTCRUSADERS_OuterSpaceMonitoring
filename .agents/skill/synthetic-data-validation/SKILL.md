---
name: synthetic-data-validation
description: Clinical, physiological and statistical plausibility checklist for auditing synthetic health datasets. Use ONLY when validating a generated CSV, reviewing pandas.describe() output or correlation matrices, or producing a validation_report.md with actionable fixes.
---

# Synthetic Data Validation

Reference checklist for the `data-validator` agent. Apply every dimension and
report in the mandatory format below.

## 1. Physiological sanity checks

- Resting heart rate within 30-200 bpm; never negative.
- HbA1c >= 3% and <= ~20%; fasting glucose > 0.
- Cognitive reaction times > 0 ms (never instantaneous).
- `N_Back_Accuracy` and quality scores within 0-100%.
- `BMI` consistent with `Weight (kg) / Height (m)^2` (tolerance ~0.5).

## 2. Expected clinical correlations

- **Cardiometabolic:** higher `BMI` -> higher systolic/diastolic BP and fasting glucose.
- **Ophthalmology:** DR-labelled rows show elevated microaneurysms/exudates vs healthy;
  `RNFL_Thickness` decreases with age; `cup_to_disc_ratio` rises with glaucoma-like profiles.
- **Neuro/behavioral:** low `Sleep_Hours` / high `Stress_Level` -> slower
  `PVT_Reaction_Time` and `Stroop_Task_Reaction_Time`, lower `N_Back_Accuracy`,
  higher `Daytime_Sleepiness`.

## 3. Population distribution

- Distributions should be normal/skewed where reality is, not perfectly uniform or linear.
- Extreme values must be a statistical minority.

## Mandatory report format (`output/validation_report.md`)

### 1. Diagnostico General
1-2 paragraphs on overall coherence.

### 2. Anomalias Fisiologicas y Estadisticas Detectadas
"Red Flags" list; explain why each is medically implausible.

### 3. Recomendaciones Accionables para el Codigo
Direct mathematical instructions for the synthesizer. Do not edit the code; state the logic to change (and, for weight-only issues, hand off to `data-configurator`).

## Optional metrics (`output/validation_metrics.json`)

Record per-column min/max/mean/std, correlation values of the checks above, and
out-of-range counts so changes can be diffed across runs.
