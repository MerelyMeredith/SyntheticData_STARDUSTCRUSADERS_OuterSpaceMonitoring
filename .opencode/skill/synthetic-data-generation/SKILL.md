---
name: synthetic-data-generation
description: Knowledge pack for generating multi-domain longitudinal synthetic health data across time with realistic sampling frequencies and per-user files.
---

# Synthetic Data Generation Skill (Longitudinal & Multi-Domain)

## Architecture
- **Per-User File Storage:** Each patient user receives their dedicated longitudinal CSV under `output/patients/<Patient_ID>.csv`.
- **Consolidated Dataset:** Aggregated observations are stored at `output/dataset.csv`.
- **Realistic Sampling & Lapses:**
  - Wearable Daily Vitals (Heart Rate, SpO2, Temp, RR, HRV) with configurable sensor drop rates.
  - Periodic Blood Pressure (every 3 to 14 days / biweekly clinic checks).
  - Fasting Glucose & HbA1c at realistic clinical intervals (weeks/months).
  - Session-Based Workouts recorded exclusively on active training days.
  - Periodic Neurocognitive batteries (Stroop, N-Back, PVT).
  - Ophthalmology Retinal Scans conducted on clinic visits.

## 4-Domain Variable Integration (Zero Information Discarded)
- **Data Bank 1:** Heart Rate, Timestamp, Body Temperature, SpO2, Respiratory Rate, Derived HRV, Derived Pulse Pressure, Derived MAP.
- **Data Bank 2:** Texture GLCM Contrast, Texture Gabor Response, Deep Features 1–3, Image Quality Score, Diabetes Duration, History of Hypertension, History of CVD, Smoking Status, Family History of Eye Disease, Visual Acuity, Medications, Ethnicity, Date of Last Eye Exam, Symptom Duration, Retinal Lesion Counts (Microaneurysms, Exudates, Hemorrhages), Retinal Disorder.
- **Data Bank 3:** Max BPM, Avg BPM, Session Duration, Calories Burned, Workout Type, Experience Level.
- **Data Bank 4:** Emotion Regulation Score, Physical Activity Level, Sleep Hours, Sleep Quality Score, Daytime Sleepiness, Stress Level, Stroop Reaction Time, N-Back Accuracy, PVT Reaction Time.
