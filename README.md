# NASA Space Apps 2026 — STARDUST CRUSADERS
## Longitudinal Synthetic Health Data Engine for Outer Space Monitoring

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Causal Architecture](https://img.shields.io/badge/architecture-causal%20cascade-brightgreen.svg)](#causal-cascade-architecture)
[![Zero Magic Numbers](https://img.shields.io/badge/parameters-zero%20magic%20numbers-orange.svg)](#zero-magic-numbers-governance)
[![Status](https://img.shields.io/badge/validation-100%25%20passed-success.svg)](output/validation_report.md)

An agentic, multi-domain, longitudinal synthetic data platform developed for **NASA Space Apps Challenge 2026**. It generates realistic patient health trajectories across time by fusing four distinct real clinical domains into an interconnected causal cascade—free of ML/GAN hallucinations, data leakage, or privacy risks.

- Fonseca Novelo Prina Meredith
- Macedo Cruz Jennifer Nicole
- Crisostomo Enciso Francisco Javier
- Castro Balbuena Angel Andres
- Triana Sanchez Yael Kristoph

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Data Sources & Citations](#data-sources--citations)
- [Causal Cascade Architecture](#causal-cascade-architecture)
- [Longitudinal Dynamics & Realistic Lapses](#longitudinal-dynamics--realistic-lapses)
- [Integrated Variables (68 Features)](#integrated-variables-68-features)
- [Agentic Architecture](#agentic-architecture)
- [Repository Structure](#repository-structure)
- [Installation & Quick Start](#installation--quick-start)
- [CLI Reference](#cli-reference)
- [Validation & Quality Assurance](#validation--quality-assurance)
- [License](#license)

---

## Overview

Astronaut health monitoring in long-duration exploration missions requires robust baselines, predictive models, and stress-testing datasets across interconnected physiological domains. However, real operational spaceflight medical logs are scarce and protected by privacy protocols.

**STARDUST CRUSADERS** solves this challenge by programmatically generating longitudinal synthetic cohorts using **parametric statistical distributions, clinical arithmetic, and strict causal propagation**. Rather than isolated cross-sectional records, it produces full daily timelines per patient with clinically grounded sampling intervals (e.g., continuous vitals, intermittent blood pressure, session-specific workouts, and periodic ophthalmic exams).

---

## Key Features

- **Longitudinal Time-Series Simulation:** Simulates autoregressive day-by-day evolution of patient vitals, fitness strain, sleep architecture, and metabolic markers.
- **Dedicated Per-User Files:** Exports an individual CSV for each patient under `output/patients/<Patient_ID>.csv` alongside a unified cohort dataset `output/dataset.csv`.
- **Clinically Realistic Sampling Frequencies & Configurable Lapses:**
  - *Daily Wearables:* Heart rate, SpO2, temperature, and HRV logged daily with configurable sensor dropout rates.
  - *Intermittent Hemodynamics:* Blood pressure is sampled at realistic intervals (every 3 to 14 days / biweekly clinic cuff checks), leaving non-measurement days sparse (`NaN`).
  - *Event-Driven Fitness:* Workout sessions (duration, calories, exercise BPM) logged exclusively on training days.
  - *Periodic Specialist Visits:* Retinal scans and cognitive batteries occur at scheduled clinical intervals.
- **100% Data Preservation:** Fully incorporates **all 68 variables** across the 4 foundational data banks without discarding any morphological, clinical, or computer-vision features.
- **Zero Magic Numbers:** Every distribution parameter, clinical multiplier, causal weight, and sampling interval is decoupled into `config/synthetic_data_config.json`.
- **Integrated Audit & Validation Engine:** Built-in medical auditor performing 11 sanity checks and evaluating a 13-pair clinical correlation matrix.

---

## Data Sources & Citations

The causal cascade and baseline distributions are modeled after four real-world datasets, cited in respective order:

1. **Data Bank 1: Human Vital Signs Dataset**  
   *URL:* [https://www.kaggle.com/datasets/nasirayub2/human-vital-sign-dataset](https://www.kaggle.com/datasets/nasirayub2/human-vital-sign-dataset)  
   *Domain:* Vital signs, continuous heart rate, timestamps, body temperature, oxygen saturation ($SpO_2$), respiratory rate, derived pulse pressure, and Mean Arterial Pressure (MAP).

2. **Data Bank 2: Multimodal Retinal Disorder Diagnosis Dataset**  
   *URL:* [https://www.kaggle.com/datasets/datasetengineer/multimodal-retinal-disorder-diagnosis-dataset](https://www.kaggle.com/datasets/datasetengineer/multimodal-retinal-disorder-diagnosis-dataset)  
   *Domain:* Clinical ophthalmology, optic disc/cup areas, cup-to-disc ratio (CDR), intraocular pressure (IOP), macular thickness, RNFL thickness, vascular tortuosity, retinal lesion counts (microaneurysms, exudates, hemorrhages), computer vision GLCM contrast, Gabor filters, deep feature embeddings 1–3, image quality, diabetes duration, systemic history, and visual acuity.

3. **Data Bank 3: Gym Members Exercise Tracking Dataset**  
   *URL:* [https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset)  
   *Domain:* Physical fitness, workout types (Strength, Cardio, Yoga, HIIT), session duration, calories burned, training heart rates (Avg & Max BPM), water intake, and experience levels.

4. **Data Bank 4: Sleep Deprivation and Cognitive Performance Dataset**  
   *URL:* [https://www.kaggle.com/datasets/sacramentotechnology/sleep-deprivation-and-cognitive-performance](https://www.kaggle.com/datasets/sacramentotechnology/sleep-deprivation-and-cognitive-performance)  
   *Domain:* Sleep duration and quality score, daytime sleepiness (Epworth), perceived stress level, emotion regulation score, physical activity level, and cognitive latency tests (Stroop reaction time, N-Back accuracy, PVT reaction time).

---

## Causal Cascade Architecture

The generation engine adheres to a strict 5-stage causal cascade ensuring biological and mathematical consistency:

```
[ Stage 1: Demographics & Morphology ]
  Age, Gender, Ethnicity, Height, Weight -> BMI, Deurenberg Fat %
                     │
                     ▼
[ Stage 2: Habits & Fitness Modifiers ]
  Workout Frequency, Activity Level -> Resting BPM & BMI Downward Modulation
                     │
                     ▼
[ Stage 3: Sleep, Stress & Neurocognition ]
  Caffeine & Exercise -> Sleep Hours & Quality -> Stress & Emotion Regulation
  Sleep Deficit & Age -> Stroop Latency, N-Back %, PVT Reaction Time
                     │
                     ▼
[ Stage 4: Metabolism & Hemodynamics ]
  BMI, Age, Stress -> Systolic & Diastolic BP, MAP, Pulse Pressure
  BMI & Sedentary Habit -> Fasting Glucose & HbA1c
  Sleep Quality & Fitness -> Heart Rate Variability (HRV)
                     │
                     ▼
[ Stage 5: Ophthalmology & Retinal Outcomes ]
  Elevated HbA1c (Diabetes) -> Microaneurysms & Exudates -> Diabetic Retinopathy (DR)
  Severe Systolic BP (HTN)  -> Hemorrhages & Vessel Tortuosity -> Hypertensive Retinopathy (HR)
  Advanced Age & IOP        -> RNFL Thinning, High CDR -> Glaucoma & AMD
```

---

## Longitudinal Dynamics & Realistic Lapses

Unlike static generators that fill every field on every row, STARDUST CRUSADERS mirrors real-world telemetry:

- **Autoregressive Markovian Trends:** Daily stress and sleep follow autoregressive processes ($S_t = 0.65 S_{t-1} + 0.35 \mu + \epsilon_t$), ensuring natural multi-day episodes rather than white noise.
- **Sparse Measurement Schedules:**
  - **Blood Pressure:** Sampled intermittently according to clinical guidelines (`blood_pressure_interval_days`: 3–14 days). Intervening days are appropriately left empty (`NaN`).
  - **Metabolic Labs:** Fasting glucose tested every 7–28 days; HbA1c tested every 60–180 days.
  - **Workout Logs:** Only present on scheduled workout days matching the patient's weekly frequency.
  - **Retinal Imaging:** Captured at baseline and scheduled multi-month follow-up visits.
- **Sensor Dropout & Lapses:** Incorporates realistic sensor dropout probabilities (`wearable_sensor_drop_rate: 0.05`, `workout_log_miss_rate: 0.04`).

---

## Integrated Variables (68 Features)

| Category | Variable Count | Features Included |
|---|:---:|---|
| **Metadata & Time** | 2 | `Patient_ID`, `Timestamp` |
| **Demographics & Morphology** | 7 | `Age`, `Gender`, `Ethnicity`, `Height_m`, `Weight_kg`, `BMI`, `Fat_Percentage` |
| **Medical Profile & History** | 7 | `Smoking_Status`, `History_Hypertension`, `History_CVD`, `Diabetes_Duration_years`, `Family_History_Eye_Disease`, `Medications`, `Risk_Category` |
| **Habits & Fitness (DB 3 + 4)** | 10 | `Workout_Frequency_days_week`, `Physical_Activity_Level`, `Experience_Level`, `Workout_Type`, `Session_Duration_hours`, `Calories_Burned`, `Avg_BPM`, `Max_BPM`, `Caffeine_Intake_cups_day`, `Water_Intake_liters` |
| **Sleep & Cognition (DB 4)** | 8 | `Sleep_Hours`, `Sleep_Quality_Score`, `Daytime_Sleepiness`, `Stress_Level`, `Emotion_Regulation_Score`, `Stroop_Task_Reaction_Time_s`, `N_Back_Accuracy_pct`, `PVT_Reaction_Time_ms` |
| **Metabolism & Vitals (DB 1)** | 11 | `Heart_Rate`, `Systolic_BP`, `Diastolic_BP`, `Derived_Pulse_Pressure`, `Derived_MAP`, `Fasting_Glucose_mg_dl`, `HbA1c_pct`, `Derived_HRV_s`, `Body_Temperature_c`, `Oxygen_Saturation_pct`, `Respiratory_Rate_bpm` |
| **Ophthalmology & Retina (DB 2)** | 23 | `Date_of_Last_Eye_Exam`, `Symptom_Duration_weeks`, `Visual_Acuity`, `Image_Quality_Score`, `Optic_Disc_Area`, `Optic_Cup_Area`, `Cup_to_Disc_Ratio`, `Intraocular_Pressure_mmhg`, `Macular_Thickness_um`, `RNFL_Thickness_um`, `Vessel_Tortuosity`, `Bifurcation_Angle_deg`, `FAZ_Area_mm2`, `Texture_GLCM_Contrast`, `Texture_Gabor_Response`, `Deep_Feature_1`, `Deep_Feature_2`, `Deep_Feature_3`, `Microaneurysms_Count`, `Exudates_Count`, `Hemorrhages_Count`, `Retinal_Disorder`, `Retinal_Disorder_Label` |

---

## Agentic Architecture

The project is structured according to an autonomous agent collaboration protocol defined in [`AGENTS.md`](AGENTS.md):

```
                        ┌─────────────────────────┐
                        │    data-configurator    │
                        │ (Subagent / JSON Owner) │
                        └────────────┬────────────┘
                                     │ config/*.json
                                     ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│     data-validator      │◄─────┤     data-synthesizer    │
│  (Auditor / Subagent)   │      │   (Primary Developer)   │
└─────────────────────────┘      └─────────────────────────┘
  output/validation_report.md       output/dataset.csv
```

- **`data-synthesizer` (Primary):** Owns `app/modules/generate.py`, implementing the arithmetic causal pipeline.
- **`data-configurator` (Subagent):** Owns `config/*.json`, defining all distributions, bounds, and weights.
- **`data-validator` (Subagent):** Owns `app/modules/validate.py`, executing automated audits and generating Markdown validation reports.

---

## Repository Structure

```
SyntheticData_STARDUSTCRUSADERS_OuterSpaceMonitoring/
├── .gitignore                      # Publication gitignore (hides raw datasets & outputs)
├── AGENTS.md                       # Project agent guidelines and operational contracts
├── opencode.json                   # OpenCode toolchain configuration
├── README.md                       # Main project documentation
├── agents/                         # Original agent system prompts (Spanish)
├── .opencode/                      # Registered OpenCode agents and skill packs
│   ├── agent/                      # data-synthesizer, data-configurator, data-validator
│   └── skill/                      # synthetic-data-generation, synthetic-data-validation
├── app/
│   ├── main.py                     # Unified CLI entry point & interactive menu
│   ├── core/
│   │   ├── paths.py                # Filesystem paths and directories
│   │   └── registry.py             # Modular command dispatcher
│   └── modules/
│       ├── configure.py            # Generates config JSON parameters
│       ├── generate.py             # Longitudinal causal generation engine
│       ├── validate.py             # Clinical and statistical auditor
│       └── preview.py              # Terminal tabular inspection
├── config/
│   └── synthetic_data_config.json  # Central causal weights and schedules
├── dataSources/                    # Raw Kaggle CSV inputs (read-only, gitignored)
│   └── .gitkeep
└── output/
    ├── .gitkeep
    ├── dataset.csv                 # Consolidated longitudinal dataset
    ├── validation_report.md        # Formal medical & statistical audit report
    └── patients/                   # Dedicated per-user longitudinal CSVs
        ├── SC-00001.csv
        ├── SC-00002.csv
        └── ...
```

---

## Installation & Quick Start

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### Setup

```powershell
# 1. Clone repository
git clone <repository-url>
cd SyntheticData_STARDUSTCRUSADERS_OuterSpaceMonitoring

# 2. Install required dependencies
pip install -r requirements.txt
# (or install directly: pip install pandas numpy)

# 3. Check environment status
python app/main.py info
```

---

## CLI Reference

The platform provides a modular CLI interface via `app/main.py`:

```powershell
# Display data sources, modules, config, and output status
python app/main.py info

# Generate or update causal parameter configuration JSON
python app/main.py configure

# Generate a longitudinal synthetic cohort:
# Produces output/dataset.csv AND individual files in output/patients/
python app/main.py generate --patients 30 --days 60 --output output/dataset.csv

# Audit the dataset against physiological bounds and clinical correlations
python app/main.py validate --input output/dataset.csv --report output/validation_report.md

# Preview records from any dataset or patient file
python app/main.py preview --input output/patients/SC-00001.csv --rows 5

# Launch interactive menu
python app/main.py
```

---

## Validation & Quality Assurance

Every generated dataset is formally audited by `app/modules/validate.py`. The full audit report is maintained at [`output/validation_report.md`](output/validation_report.md).

### Key Audit Metrics (Latest Benchmark: 30 Patients × 60 Days = 1,800 Observations)

- **Sanity Checks Passed:** **11 / 11 (100%)**
  - $\checkmark$ Zero missing demographic or identification fields
  - $\checkmark$ Exact mathematical BMI formula consistency ($BMI = \frac{Weight}{Height^2}$)
  - $\checkmark$ Hemodynamic consistency: $Systolic > Diastolic + 15\text{ mmHg}$ (0 inverted cases)
  - $\checkmark$ All vitals within human survival bounds ($SpO_2 \in [94\%, 100\%]$, $BPM \in [55, 87]$)
  - $\checkmark$ Intermittent BP sampling verified at 14.6% observation rate
  - $\checkmark$ Individual per-user files verified (30 / 30 files created)

### Clinical Correlation Verification (13 / 13 Physiologically Validated)

| Clinical Relationship | Observed Pearson ($r$) | Expected Sign | Clinical Interpretation | Status |
|---|:---:|:---:|---|:---:|
| **BMI vs Systolic BP** | `+0.401` | $> 0$ | Adiposity increases peripheral vascular resistance | **PASS** ✅ |
| **BMI vs Fasting Glucose** | `+0.414` | $> 0$ | Adiposity induces metabolic insulin resistance | **PASS** ✅ |
| **Age vs Systolic BP** | `+0.450` | $> 0$ | Arterial stiffening with advancing age | **PASS** ✅ |
| **Age vs RNFL Thickness** | `-0.539` | $< 0$ | Natural nerve fiber thinning across decades | **PASS** ✅ |
| **Sleep Duration vs Stress** | `-0.235` | $< 0$ | Adequate sleep buffers perceived stress | **PASS** ✅ |
| **Sleep Duration vs PVT Reaction Time** | `-0.735` | $< 0$ | Sleep deprivation severely impairs alertness | **PASS** ✅ |
| **Sleep Quality vs Stroop Latency** | `-0.450` | $< 0$ | Restorative sleep enhances executive control | **PASS** ✅ |
| **Sleep Quality vs N-Back Accuracy** | `+0.429` | $> 0$ | Working memory accuracy benefits from sleep | **PASS** ✅ |
| **HbA1c vs Microaneurysms** | `+0.841` | $> 0$ | Diabetic microangiopathy drives retinal lesions | **PASS** ✅ |
| **Systolic BP vs Hemorrhages** | `+0.598` | $> 0$ | Hypertensive shearing causes vascular leaks | **PASS** ✅ |
| **Stress Level vs Derived HRV** | `-0.318` | $< 0$ | Sympathetic activation dampens vagal HRV | **PASS** ✅ |
| **Workout Frequency vs Resting Heart Rate** | `-0.588` | $< 0$ | Aerobic adaptation induces athletic bradycardia | **PASS** ✅ |
| **Stress Level vs Emotion Regulation** | `-0.291` | $< 0$ | Chronic stress degrades affective regulation | **PASS** ✅ |

---

## License

Developed for the **NASA Space Apps Challenge 2026** by the **STARDUST CRUSADERS** team. Distributed under the MIT License.


# Launch interactive menu
python app/main.py
```

---

## Validation & Quality Assurance

Every generated dataset is formally audited by `app/modules/validate.py`. The full audit report is maintained at [`output/validation_report.md`](output/validation_report.md).

### Key Audit Metrics (Latest Benchmark: 30 Patients × 60 Days = 1,800 Observations)

- **Sanity Checks Passed:** **11 / 11 (100%)**
  - $\checkmark$ Zero missing demographic or identification fields
  - $\checkmark$ Exact mathematical BMI formula consistency ($BMI = \frac{Weight}{Height^2}$)
  - $\checkmark$ Hemodynamic consistency: $Systolic > Diastolic + 15\text{ mmHg}$ (0 inverted cases)
  - $\checkmark$ All vitals within human survival bounds ($SpO_2 \in [94\%, 100\%]$, $BPM \in [55, 87]$)
  - $\checkmark$ Intermittent BP sampling verified at 14.6% observation rate
  - $\checkmark$ Individual per-user files verified (30 / 30 files created)

### Clinical Correlation Verification (13 / 13 Physiologically Validated)

| Clinical Relationship | Observed Pearson ($r$) | Expected Sign | Clinical Interpretation | Status |
|---|:---:|:---:|---|:---:|
| **BMI vs Systolic BP** | `+0.401` | $> 0$ | Adiposity increases peripheral vascular resistance | **PASS** ✅ |
| **BMI vs Fasting Glucose** | `+0.414` | $> 0$ | Adiposity induces metabolic insulin resistance | **PASS** ✅ |
| **Age vs Systolic BP** | `+0.450` | $> 0$ | Arterial stiffening with advancing age | **PASS** ✅ |
| **Age vs RNFL Thickness** | `-0.539` | $< 0$ | Natural nerve fiber thinning across decades | **PASS** ✅ |
| **Sleep Duration vs Stress** | `-0.235` | $< 0$ | Adequate sleep buffers perceived stress | **PASS** ✅ |
| **Sleep Duration vs PVT Reaction Time** | `-0.735` | $< 0$ | Sleep deprivation severely impairs alertness | **PASS** ✅ |
| **Sleep Quality vs Stroop Latency** | `-0.450` | $< 0$ | Restorative sleep enhances executive control | **PASS** ✅ |
| **Sleep Quality vs N-Back Accuracy** | `+0.429` | $> 0$ | Working memory accuracy benefits from sleep | **PASS** ✅ |
| **HbA1c vs Microaneurysms** | `+0.841` | $> 0$ | Diabetic microangiopathy drives retinal lesions | **PASS** ✅ |
| **Systolic BP vs Hemorrhages** | `+0.598` | $> 0$ | Hypertensive shearing causes vascular leaks | **PASS** ✅ |
| **Stress Level vs Derived HRV** | `-0.318` | $< 0$ | Sympathetic activation dampens vagal HRV | **PASS** ✅ |
| **Workout Frequency vs Resting Heart Rate** | `-0.588` | $< 0$ | Aerobic adaptation induces athletic bradycardia | **PASS** ✅ |
| **Stress Level vs Emotion Regulation** | `-0.291` | $< 0$ | Chronic stress degrades affective regulation | **PASS** ✅ |

---

## License

Developed for the **NASA Space Apps Challenge 2026** by the **STARDUST CRUSADERS** team. Distributed under the MIT License.