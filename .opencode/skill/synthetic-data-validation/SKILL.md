---
name: synthetic-data-validation
description: Knowledge pack for clinical, statistical, and longitudinal auditing of synthetic patient datasets.
---

# Synthetic Data Validation Skill

## Audit Dimensions
1. **Core Patient & Temporal Integrity:**
   - 100% completeness for Patient_ID, Timestamp, and core demographics.
   - Mathematical identity check: $BMI = \frac{\text{Weight (kg)}}{(\text{Height (m)})^2}$.
2. **Complete 4-Domain Variable Coverage:**
   - Verifies inclusion and population of all variables from Data Banks 1, 2, 3, and 4 without dropping features.
3. **Hemodynamic & Physiological Integrity:**
   - Non-null blood pressure records strictly verify $\text{Systolic BP} > \text{Diastolic BP} + 15$.
   - Measured vitals, glucose, HbA1c, and cognitive scores remain strictly within biological limits.
4. **Longitudinal Scheduling & Lapses:**
   - Audits that Blood Pressure is intermittent (handful of days to biweekly).
   - Audits that workout sessions are recorded only on training days.
   - Audits that specialized ophthalmic exams occur at clinical intervals.
   - Verifies individual per-user CSV files in `output/patients/`.
5. **Correlation Matrix:**
   - Evaluates Pearson correlation signs and magnitudes across cardiometabolic, neurobehavioral, and ophthalmic relationships.
