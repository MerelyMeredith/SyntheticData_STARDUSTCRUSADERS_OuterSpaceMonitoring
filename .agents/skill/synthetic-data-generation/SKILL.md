---
name: synthetic-data-generation
description: Data dictionary, causal cascade rules and column schema for generating synthetic health data. Use ONLY when generating or modifying synthetic patient records that fuse vitals, retinal/ophthalmology, fitness and sleep domains, or when mapping columns between dataSources/*.csv and the generated output.
---

# Synthetic Data Generation

Reference knowledge for the `data-synthesizer` agent. Load this when writing the
generation logic so the causal cascade and the output schema stay consistent.

## Source datasets (`dataSources/`)

| File | Domain | Key columns |
| --- | --- | --- |
| `DataBank1_human_vital_signs_dataset_2024.csv` | Vitals | Heart Rate, Respiratory Rate, Body Temperature, Oxygen Saturation, Systolic/Diastolic Blood Pressure, Age, Gender, Weight (kg), Height (m), Derived_HRV, Derived_Pulse_Pressure, Derived_BMI, Derived_MAP, Risk Category |
| `DataBank2_retinal_disorders_dataset.csv` | Ophthalmology | optic_disc_area, optic_cup_area, cup_to_disc_ratio, exudates_count, hemorrhages_count, microaneurysms_count, vessel_tortuosity, bifurcation_angle, faz_area, macular_thickness, rnfl_thickness, fasting_glucose, hba1c, diabetes_duration, retinal_disorder |
| `DataBank3_gym_members_exercise_tracking.csv` | Fitness | Age, Gender, Weight (kg), Height (m), Max_BPM, Avg_BPM, Resting_BPM, Calories_Burned, Workout_Type, Fat_Percentage, Water_Intake (liters), Workout_Frequency (days/week), Experience_Level, BMI |
| `DataBank4_sleep_deprivation_dataset_detailed.csv` | Sleep/Cognition | Sleep_Hours, Sleep_Quality_Score, Daytime_Sleepiness, Stroop_Task_Reaction_Time, N_Back_Accuracy, Emotion_Regulation_Score, PVT_Reaction_Time, Age, Gender, BMI, Caffeine_Intake, Physical_Activity_Level, Stress_Level |

## Causal cascade (strict order)

Generate in this order so downstream variables can depend on upstream ones.

1. **Demographics / morphology** — `Age` (18-90), `Gender`, `Height`, `Weight`.
   Compute `BMI` from height/weight, derive base `Fat_Percentage` adjusted by age and gender.
2. **Habits / fitness** — `Workout_Frequency`, `Caffeine_Intake`, `Water_Intake`.
   Nudge `Resting_BPM`, `Fat_Percentage`, `BMI` down as `Workout_Frequency` rises.
3. **Sleep / stress / cognition** — `Sleep_Hours`, `Sleep_Quality_Score`
   (penalized by high caffeine, low workout). Derive `Stress_Level` inversely to
   sleep quality and activity. Cognitive metrics (`Stroop_Task_Reaction_Time`,
   `N_Back_Accuracy`, `PVT_Reaction_Time`, `Daytime_Sleepiness`) penalized by poor sleep and high age.
4. **Metabolism / vitals** — `Systolic_BP`, `Diastolic_BP` (rise with BMI, stress, age);
   `Fasting_Glucose`, `HbA1c` (rise with BMI and sedentary behavior); `Derived_HRV`
   (up with sleep quality and fitness, down with stress and age).
5. **Retinal outcomes** — high `HbA1c` -> more `Microaneurysms_Count` and
   `Retinal_Disorder = 1` (DR); high systolic BP -> more `Hemorrhages_Count` and
   `Retinal_Disorder = 4` (HR); high `Age` -> lower `RNFL_Thickness` and higher
   probability of `Retinal_Disorder = 3` (AMD). `0` = healthy.

## Hard rules

- No ML / GANs. Pure logic + `numpy` distributions.
- Read every weight, mean, std and bound from `config/*.json` (owned by `data-configurator`). No magic numbers.
- Clamp to physiological ranges: cognition 0-100%, BPM > 0, HbA1c >= 3, reaction times > 0.
- Expose `generate_synthetic_health_data(num_records) -> pandas.DataFrame`.
- Wrap the module entry point as `run(context) -> int` (see `app/core/registry.py`).
