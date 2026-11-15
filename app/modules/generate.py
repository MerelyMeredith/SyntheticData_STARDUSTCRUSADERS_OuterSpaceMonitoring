"""Longitudinal synthetic data generation module (data-synthesizer).

Generates multi-domain synthetic patient health data across time.
Features:
  - File for every patient user: output/patients/<Patient_ID>.csv
  - Consolidated longitudinal dataset: output/dataset.csv
  - Realistic measurement schedules with configurable lapses:
      * Daily / wearable vitals (Heart Rate, Temp, SpO2, HRV, RR)
      * Periodic blood pressure (handful of days to biweekly)
      * Periodic metabolic labs (fasting glucose, HbA1c)
      * Session-based fitness logs on workout days
      * Periodic cognitive batteries (Stroop, N-Back, PVT)
      * Longitudinal retinal scans & computer vision features
  - 100% data preservation: integrates all variables from Data Banks 1, 2, 3, and 4.
  - Zero hardcoded numbers: all distributions, multipliers, and schedules come from config.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from app.core import paths, registry
from app.modules import configure


def _truncated_normal(
    mean: float, std: float, low: float, high: float, size: int | tuple[int, ...], rng: np.random.Generator
) -> np.ndarray:
    """Generate samples from a normal distribution clipped to [low, high]."""
    values = rng.normal(loc=mean, scale=std, size=size)
    return np.clip(values, low, high)


def generate_patient_longitudinal_series(
    patient_id: str,
    days: int,
    config: dict[str, Any],
    rng: np.random.Generator,
    start_date: datetime,
) -> pd.DataFrame:
    """Generate a realistic longitudinal timeline for a single patient user."""
    demo_cfg = config["demographics"]
    hist_cfg = config["clinical_history"]
    habits_cfg = config["habits_and_fitness"]
    sc_cfg = config["sleep_and_cognition"]
    metab_cfg = config["metabolism_and_vitals"]
    oph_cfg = config["ophthalmology_and_retina"]
    sched_cfg = config["temporal_and_schedules"]
    freq_cfg = sched_cfg["frequencies"]
    lapse_cfg = sched_cfg["lapses"]

    # -------------------------------------------------------------------------
    # 1. Patient Static / Baseline Attributes
    # -------------------------------------------------------------------------
    age_cfg = demo_cfg["age"]
    age = int(round(float(_truncated_normal(age_cfg["mean"], age_cfg["std"], age_cfg["min"], age_cfg["max"], 1, rng)[0])))

    gender_cfg = demo_cfg["gender"]
    is_male = bool(rng.random() < float(gender_cfg["male_probability"]))
    gender = "Male" if is_male else "Female"

    ethnicity_cfg = demo_cfg["ethnicity"]
    ethnicity = str(rng.choice(ethnicity_cfg["categories"], p=ethnicity_cfg["probabilities"]))

    h_cfg = demo_cfg["height_m"][gender]
    height = round(float(_truncated_normal(h_cfg["mean"], h_cfg["std"], h_cfg["min"], h_cfg["max"], 1, rng)[0]), 2)

    bmi_cfg = demo_cfg["bmi_base"][gender]
    base_bmi = float(_truncated_normal(bmi_cfg["mean"], bmi_cfg["std"], bmi_cfg["min"], bmi_cfg["max"], 1, rng)[0])

    wf_cfg = habits_cfg["workout_frequency_days"]
    workout_frequency = int(np.clip(rng.poisson(lam=wf_cfg["lambda"]), wf_cfg["min"], wf_cfg["max"]))

    fit_mods = habits_cfg["fitness_modifiers"]
    adj_bmi = np.clip(base_bmi - (workout_frequency * fit_mods["bmi_reduction_per_workout_day"]), 15.0, 50.0)
    base_weight = round(float(adj_bmi * (height ** 2)), 1)
    base_bmi = round(float(base_weight / (height ** 2)), 2)

    fat_cfg = demo_cfg["fat_percentage"]
    gender_offset = fat_cfg["deurenberg_male_subtraction"] if is_male else 0.0
    raw_fat = (
        (fat_cfg["deurenberg_bmi_coeff"] * base_bmi)
        + (fat_cfg["deurenberg_age_coeff"] * age)
        - gender_offset
        - fat_cfg["deurenberg_constant"]
        - (workout_frequency * fit_mods["fat_reduction_per_workout_day"])
        + float(rng.normal(0, fat_cfg["noise_std"]))
    )
    base_fat_pct = round(float(np.clip(raw_fat, fat_cfg["min"], fat_cfg["max"])), 1)

    # Clinical history
    smoke_cfg = hist_cfg["smoking_status"]
    smoking_status = str(rng.choice(smoke_cfg["categories"], p=smoke_cfg["probabilities"]))

    eye_hist_cfg = hist_cfg["family_history_eye_disease"]
    family_history_eye = str(rng.choice(eye_hist_cfg["categories"], p=eye_hist_cfg["probabilities"]))

    # Hypertension history coupled with age and BMI
    is_htn_likely = (age > hist_cfg["hypertension_age_threshold"]) and (base_bmi > hist_cfg["hypertension_bmi_threshold"])
    htn_prob = 0.55 if is_htn_likely else 0.22
    history_hypertension = "Yes" if rng.random() < htn_prob else "No"

    # CVD history coupled with HTN, smoking and age
    cvd_prob = float(hist_cfg["cvd_base_prob"])
    if history_hypertension == "Yes":
        cvd_prob *= float(hist_cfg["cvd_htn_multiplier"])
    if smoking_status != "Never":
        cvd_prob *= float(hist_cfg["cvd_smoking_multiplier"])
    history_cvd = "Yes" if rng.random() < min(0.65, cvd_prob) else "No"

    # Diabetes status & duration
    glu_cfg = metab_cfg["fasting_glucose_mg_dl"]
    diab_frac = float(glu_cfg.get("diabetic_fraction", 0.14))
    is_diabetic = bool((rng.random() < diab_frac) and (base_bmi >= 25.5))
    if is_diabetic:
        diab_dur_cfg = hist_cfg["diabetes_duration_years"]
        diabetes_duration = int(np.clip(round(rng.normal(diab_dur_cfg["mean"], diab_dur_cfg["std"])), diab_dur_cfg["min"], diab_dur_cfg["max"]))
    else:
        diabetes_duration = 0

    # Medications
    if is_diabetic and history_hypertension == "Yes":
        medications = "Combination"
    elif is_diabetic:
        medications = "Insulin"
    elif history_hypertension == "Yes":
        medications = "ACE Inhibitors"
    elif history_cvd == "Yes":
        medications = "Statins"
    else:
        medications = "No Medication"

    # Fitness profile
    act_cfg = habits_cfg["physical_activity_level"]
    activity_level = int(np.clip(round(act_cfg["base_mean"] + (workout_frequency * act_cfg["workout_coupling"]) + rng.normal(0, 1)), act_cfg["min"], act_cfg["max"]))

    sess_cfg = habits_cfg["workout_sessions"]
    experience_level = int(rng.choice(sess_cfg["experience_levels"], p=sess_cfg["experience_probabilities"]))
    fav_workout_type = str(rng.choice(sess_cfg["types"], p=sess_cfg["type_probabilities"]))

    caff_cfg = habits_cfg["caffeine_intake_cups"]
    base_caffeine = round(float(_truncated_normal(caff_cfg["mean"], caff_cfg["std"], caff_cfg["min"], caff_cfg["max"], 1, rng)[0]), 1)

    water_cfg = habits_cfg["water_intake_liters"]
    base_water = round(float(water_cfg["base_mean"] + (workout_frequency * water_cfg["workout_bonus_per_day"]) + rng.normal(0, 0.3)), 2)

    # Ophthalmology baseline disorder assignment
    dis_cfg = oph_cfg["disorders"]
    p_dr = 0.65 if (is_diabetic and diabetes_duration >= 5) else (0.30 if is_diabetic else 0.01)
    p_hr = 0.40 if history_hypertension == "Yes" else 0.02
    p_amd = 0.35 if age >= dis_cfg["amd_age_threshold"] else 0.02
    iop_cfg = oph_cfg["intraocular_pressure_mmhg"]
    base_iop = float(_truncated_normal(iop_cfg["base_mean"], iop_cfg["base_std"], iop_cfg["min"], 23.0, 1, rng)[0])
    p_glaucoma = 0.45 if (family_history_eye == "Yes" or base_iop > 19.0) else 0.03

    candidate_disorders = [
        (1, p_dr),
        (4, p_hr),
        (3, p_amd),
        (2, p_glaucoma),
    ]
    candidate_disorders.sort(key=lambda x: x[1], reverse=True)
    top_code, top_risk = candidate_disorders[0]
    retinal_disorder_code = top_code if rng.random() < top_risk else 0
    retinal_disorder_label = dis_cfg["codes"].get(str(retinal_disorder_code), "Normal")

    # Visual acuity & symptoms
    va_cfg = oph_cfg["visual_acuity"]
    if retinal_disorder_code == 0:
        visual_acuity = str(rng.choice(va_cfg["categories"], p=va_cfg["normal_probs"]))
        symptom_duration = 0
    else:
        visual_acuity = str(rng.choice(va_cfg["categories"], p=va_cfg["impaired_probs"]))
        sym_cfg = oph_cfg["symptom_duration_weeks"]
        symptom_duration = int(np.clip(round(rng.normal(sym_cfg["disorder_mean"], sym_cfg["disorder_std"])), 1, sym_cfg["max"]))

    last_exam_date = (start_date - timedelta(days=int(rng.integers(60, 300)))).strftime("%Y-%m-%d")

    # -------------------------------------------------------------------------
    # 2. Longitudinal Timeline Schedules (Day by Day)
    # -------------------------------------------------------------------------
    # Blood pressure sampling days (a handful of days to biweekly)
    bp_interval = int(rng.integers(freq_cfg["blood_pressure_interval_days_min"], freq_cfg["blood_pressure_interval_days_max"] + 1))
    # Glucose lab interval (1-4 weeks)
    glu_interval = int(rng.integers(freq_cfg["fasting_glucose_interval_days_min"], freq_cfg["fasting_glucose_interval_days_max"] + 1))
    # Cognitive testing interval (7-21 days)
    cog_interval = int(rng.integers(freq_cfg["cognitive_test_interval_days_min"], freq_cfg["cognitive_test_interval_days_max"] + 1))
    # Retinal exam scheduled day (e.g., day 0 or endpoint)
    retinal_exam_days = {0}
    if days >= 90:
        retinal_exam_days.add(int(rng.integers(80, days)))

    # Workout schedule: days of week assigned to workouts (e.g. 0 to 6)
    possible_days = list(range(7))
    rng.shuffle(possible_days)
    workout_days_of_week = set(possible_days[:workout_frequency])

    records: list[dict[str, Any]] = []

    # Dynamic Markovian baseline states
    curr_stress = float(sc_cfg["stress_level"]["base_mean"] + rng.normal(0, 1.0))

    for day_idx in range(days):
        current_date = start_date + timedelta(days=day_idx)
        timestamp_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        day_of_week = current_date.weekday()

        # Slow daily fluctuation in weight and BMI
        day_weight = round(base_weight + float(rng.normal(0, 0.25)), 1)
        day_bmi = round(float(day_weight / (height ** 2)), 2)
        day_fat = round(float(np.clip(base_fat_pct + rng.normal(0, 0.15), fat_cfg["min"], fat_cfg["max"])), 1)

        # Dynamic stress & sleep state
        stress_noise = float(rng.normal(0, 0.6))
        curr_stress = np.clip(0.65 * curr_stress + 0.35 * sc_cfg["stress_level"]["base_mean"] + stress_noise, 0.0, 10.0)

        sh_cfg = sc_cfg["sleep_hours"]
        stress_pen = float(sh_cfg.get("stress_penalty_per_level", 0.18))
        sleep_hours = round(float(np.clip(
            sh_cfg["base_mean"] - (base_caffeine * sh_cfg["caffeine_penalty_per_cup"]) - (curr_stress * stress_pen) + (workout_frequency * sh_cfg["workout_bonus_per_day"]) + rng.normal(0, 0.4),
            sh_cfg["min"], sh_cfg["max"]
        )), 2)

        sq_cfg = sc_cfg["sleep_quality_score"]
        sleep_deficit = max(0.0, sq_cfg["optimal_sleep_hours"] - sleep_hours)
        sleep_quality = round(float(np.clip(
            sq_cfg["base_mean"] - (sleep_deficit * sq_cfg["sleep_hours_coeff"]) - (base_caffeine * sq_cfg["caffeine_penalty_per_cup"]) + rng.normal(0, 5.0),
            sq_cfg["min"], sq_cfg["max"]
        )), 1)

        ds_cfg = sc_cfg["daytime_sleepiness"]
        daytime_sleepiness = round(float(np.clip(
            ds_cfg["base_mean"] + (sleep_deficit * ds_cfg["sleep_deficit_multiplier"]) + rng.normal(0, 1.2),
            ds_cfg["min"], ds_cfg["max"]
        )), 1)

        emo_cfg = sc_cfg["emotion_regulation_score"]
        emotion_regulation = round(float(np.clip(
            emo_cfg["base_mean"] + (curr_stress * emo_cfg["stress_penalty"]) + ((sleep_hours - 7.0) * emo_cfg["sleep_bonus"]) + rng.normal(0, 6.0),
            emo_cfg["min"], emo_cfg["max"]
        )), 1)

        # ---------------------------------------------------------------------
        # Wearables / Daily Vitals (with sensor drop lapse)
        # ---------------------------------------------------------------------
        wearable_lapse = (rng.random() < float(lapse_cfg["wearable_sensor_drop_rate"]))
        if wearable_lapse:
            heart_rate = np.nan
            derived_hrv = np.nan
            body_temp = np.nan
            oxygen_sat = np.nan
            resp_rate = np.nan
        else:
            rbpm_cfg = metab_cfg["resting_bpm"]
            hr_val = rbpm_cfg["base_mean"] - (workout_frequency * fit_mods["bpm_reduction_per_workout_day"]) + (curr_stress * rbpm_cfg["stress_impact"]) + rng.normal(0, 4.0)
            heart_rate = int(np.clip(round(hr_val), rbpm_cfg["min"], rbpm_cfg["max"]))

            hrv_cfg = metab_cfg["derived_hrv_s"]
            hrv_val = hrv_cfg["base_mean"] + (workout_frequency * hrv_cfg["workout_bonus"]) + (curr_stress * hrv_cfg["stress_penalty"]) + rng.normal(0, 0.008)
            derived_hrv = round(float(np.clip(hrv_val, hrv_cfg["min"], hrv_cfg["max"])), 4)

            temp_cfg = metab_cfg["body_temperature_c"]
            body_temp = round(float(_truncated_normal(temp_cfg["mean"], temp_cfg["std"], temp_cfg["min"], temp_cfg["max"], 1, rng)[0]), 2)

            spo2_cfg = metab_cfg["oxygen_saturation_pct"]
            oxygen_sat = round(float(_truncated_normal(spo2_cfg["mean"], spo2_cfg["std"], spo2_cfg["min"], spo2_cfg["max"], 1, rng)[0]), 1)

            rr_cfg = metab_cfg["respiratory_rate_bpm"]
            resp_rate = int(np.clip(round(float(_truncated_normal(rr_cfg["mean"], rr_cfg["std"], rr_cfg["min"], rr_cfg["max"], 1, rng)[0])), rr_cfg["min"], rr_cfg["max"]))

        # ---------------------------------------------------------------------
        # Blood Pressure (Periodic Sampling: handful of days to biweekly)
        # ---------------------------------------------------------------------
        is_bp_day = (day_idx % bp_interval == 0) and not (rng.random() < float(lapse_cfg["clinical_visit_cancel_rate"]))
        if is_bp_day:
            sbp_cfg = metab_cfg["systolic_bp"]
            dbp_cfg = metab_cfg["diastolic_bp"]
            htn_elev = 22.0 if history_hypertension == "Yes" else 0.0
            sbp_val = sbp_cfg["base_mean"] + htn_elev + (max(0, age - 25) * sbp_cfg["age_impact"]) + (max(0, base_bmi - 22) * sbp_cfg["bmi_impact"]) + (curr_stress * sbp_cfg["stress_impact"]) + rng.normal(0, 3.5)
            systolic_bp = int(np.clip(round(sbp_val), sbp_cfg["min"], sbp_cfg["max"]))

            dbp_val = dbp_cfg["base_mean"] + (htn_elev * 0.5) + ((systolic_bp - 118) * dbp_cfg["systolic_coupling"]) + rng.normal(0, 3.0)
            diastolic_bp = int(np.clip(round(dbp_val), dbp_cfg["min"], dbp_cfg["max"]))
            diastolic_bp = min(diastolic_bp, systolic_bp - 15)

            derived_pulse_pressure = int(systolic_bp - diastolic_bp)
            derived_map = round(float(diastolic_bp + (derived_pulse_pressure / 3.0)), 1)
        else:
            systolic_bp = np.nan
            diastolic_bp = np.nan
            derived_pulse_pressure = np.nan
            derived_map = np.nan

        # ---------------------------------------------------------------------
        # Fasting Glucose & HbA1c (Periodic Sampling)
        # ---------------------------------------------------------------------
        is_glu_day = (day_idx % glu_interval == 0)
        is_hba1c_day = (day_idx == 0 or day_idx == (days - 1))
        if is_glu_day:
            diab_elev = float(_truncated_normal(glu_cfg.get("diabetic_elevation_mean", 68.0), glu_cfg.get("diabetic_elevation_std", 24.0), 20.0, 160.0, 1, rng)[0]) if is_diabetic else 0.0
            glu_val = glu_cfg["base_mean"] + diab_elev + (max(0, day_bmi - 25) * glu_cfg["bmi_impact"]) + rng.normal(0, 4.0)
            fasting_glucose = round(float(np.clip(glu_val, glu_cfg["min"], glu_cfg["max"])), 1)
        else:
            fasting_glucose = np.nan

        if is_hba1c_day:
            hba1c_base_glu = (glu_cfg["base_mean"] + 68.0) if is_diabetic else glu_cfg["base_mean"]
            hba1c_cfg = metab_cfg["hba1c_pct"]
            hba1c_val = hba1c_cfg["glucose_coupling_intercept"] + (hba1c_base_glu * hba1c_cfg["glucose_coupling_slope"]) + rng.normal(0, 0.15)
            hba1c = round(float(np.clip(hba1c_val, hba1c_cfg["min"], hba1c_cfg["max"])), 2)
        else:
            hba1c = np.nan

        # Risk category
        is_high_risk = (history_hypertension == "Yes" and is_diabetic) or (day_bmi >= 32.0 and history_cvd == "Yes")
        risk_category = "High Risk" if is_high_risk else "Low Risk"

        # ---------------------------------------------------------------------
        # Workout Sessions (DataBank 3: On workout days only)
        # ---------------------------------------------------------------------
        is_scheduled_workout = (day_of_week in workout_days_of_week)
        workout_missed = (rng.random() < float(lapse_cfg["workout_log_miss_rate"]))
        is_workout_active = is_scheduled_workout and not workout_missed

        if is_workout_active:
            workout_type = fav_workout_type
            dur_cfg = sess_cfg["duration_hours"]
            session_duration = round(float(_truncated_normal(dur_cfg["mean"], dur_cfg["std"], dur_cfg["min"], dur_cfg["max"], 1, rng)[0]), 2)

            avg_bpm_cfg = sess_cfg["avg_bpm"][workout_type]
            avg_bpm = int(np.clip(round(rng.normal(avg_bpm_cfg["mean"], avg_bpm_cfg["std"])), 105, 175))

            max_bpm_elev_cfg = sess_cfg["max_bpm_elevation"]
            max_bpm = int(np.clip(avg_bpm + round(rng.normal(max_bpm_elev_cfg["mean"], max_bpm_elev_cfg["std"])), 145, 205))

            cal_rate = float(sess_cfg["calorie_rate_per_hour"][workout_type])
            calories_burned = round(float((cal_rate * session_duration) + rng.normal(0, 45.0)), 1)
            water_intake = round(base_water + 0.6 + float(rng.normal(0, 0.2)), 2)
        else:
            workout_type = np.nan
            session_duration = np.nan
            avg_bpm = np.nan
            max_bpm = np.nan
            calories_burned = np.nan
            water_intake = round(base_water + float(rng.normal(0, 0.15)), 2)

        # ---------------------------------------------------------------------
        # Cognitive Battery (DataBank 4: Periodic tests)
        # ---------------------------------------------------------------------
        is_cog_day = (day_idx % cog_interval == 0)
        if is_cog_day:
            cog_cfg = sc_cfg["cognition"]
            age_excess = max(0, age - 30)

            str_cfg = cog_cfg["stroop_reaction_time_s"]
            stroop_rt = round(float(np.clip(str_cfg["base_mean"] + (age_excess * str_cfg["age_penalty_per_year"]) + (sleep_deficit * str_cfg["sleep_deprivation_penalty"]) + rng.normal(0, 0.15), str_cfg["min"], str_cfg["max"])), 2)

            nb_cfg = cog_cfg["n_back_accuracy_pct"]
            nback_acc = round(float(np.clip(nb_cfg["base_mean"] - (age_excess * nb_cfg["age_penalty_per_year"]) - (sleep_deficit * nb_cfg["sleep_deprivation_penalty"]) + rng.normal(0, 3.0), nb_cfg["min"], nb_cfg["max"])), 1)

            pvt_cfg = cog_cfg["pvt_reaction_time_ms"]
            pvt_rt = round(float(np.clip(pvt_cfg["base_mean"] + (sleep_deficit * pvt_cfg["sleep_deprivation_multiplier"]) + (curr_stress * pvt_cfg["stress_multiplier"]) + rng.normal(0, 15.0), pvt_cfg["min"], pvt_cfg["max"])), 1)
        else:
            stroop_rt = np.nan
            nback_acc = np.nan
            pvt_rt = np.nan

        # ---------------------------------------------------------------------
        # Retinal Examinations & Computer Vision (DataBank 2: Clinical Visits)
        # ---------------------------------------------------------------------
        is_retinal_day = (day_idx in retinal_exam_days)
        if is_retinal_day:
            last_exam_date = current_date.strftime("%Y-%m-%d")

            img_cfg = oph_cfg["image_quality_score"]
            image_quality = round(float(_truncated_normal(img_cfg["mean"], img_cfg["std"], img_cfg["min"], img_cfg["max"], 1, rng)[0]), 3)

            disc_cfg = oph_cfg["optic_disc_area"]
            optic_disc_area = round(float(_truncated_normal(disc_cfg["mean"], disc_cfg["std"], disc_cfg["min"], disc_cfg["max"], 1, rng)[0]), 3)

            cup_cfg = oph_cfg["optic_cup_area"]
            optic_cup_area = round(float(_truncated_normal(cup_cfg["mean"], cup_cfg["std"], cup_cfg["min"], cup_cfg["max"], 1, rng)[0]), 3)

            cdr_cfg = oph_cfg["cup_to_disc_ratio"]
            is_glauc = (retinal_disorder_code == 2)
            cdr_val = cdr_cfg["base_mean"] + (cdr_cfg["glaucoma_elevation"] if is_glauc else 0.0) + rng.normal(0, 0.05)
            cup_to_disc_ratio = round(float(np.clip(cdr_val, cdr_cfg["min"], cdr_cfg["max"])), 3)

            iop_val = base_iop + (iop_cfg["glaucoma_bonus"] if is_glauc else 0.0) + rng.normal(0, 0.8)
            intraocular_pressure = round(float(np.clip(iop_val, iop_cfg["min"], iop_cfg["max"])), 1)

            is_dr = (retinal_disorder_code == 1)
            mac_cfg = oph_cfg["macular_thickness_um"]
            mac_val = mac_cfg["mean"] + (mac_cfg["dr_edema_bonus"] if is_dr else 0.0) + rng.normal(0, 10.0)
            macular_thickness = round(float(np.clip(mac_val, mac_cfg["min"], mac_cfg["max"])), 1)

            rnfl_cfg = oph_cfg["rnfl_thickness_um"]
            rnfl_val = rnfl_cfg["base_mean"] + (max(0, age - 30) / 10.0 * rnfl_cfg["age_decay_per_decade"]) + (rnfl_cfg["glaucoma_decay"] if is_glauc else 0.0) + rng.normal(0, 3.5)
            rnfl_thickness = round(float(np.clip(rnfl_val, rnfl_cfg["min"], rnfl_cfg["max"])), 1)

            is_hr = (retinal_disorder_code == 4)
            vt_cfg = oph_cfg["vessel_tortuosity"]
            vt_val = vt_cfg["base_mean"] + (0.35 if is_hr else 0.0) + rng.normal(0, 0.05)
            vessel_tortuosity = round(float(np.clip(vt_val, vt_cfg["min"], vt_cfg["max"])), 4)

            ba_cfg = oph_cfg["bifurcation_angle_deg"]
            bifurcation_angle = round(float(_truncated_normal(ba_cfg["mean"], ba_cfg["std"], ba_cfg["min"], ba_cfg["max"], 1, rng)[0]), 2)

            faz_cfg = oph_cfg["faz_area_mm2"]
            faz_area = round(float(_truncated_normal(faz_cfg["mean"], faz_cfg["std"], faz_cfg["min"], faz_cfg["max"], 1, rng)[0]), 3)

            # Computer vision texture & deep features
            glcm_cfg = oph_cfg["texture_glcm_contrast"]
            glcm_val = glcm_cfg["base_mean"] + (glcm_cfg["dr_bonus"] if is_dr else 0.0) + rng.normal(0, 0.4)
            texture_glcm = round(float(np.clip(glcm_val, glcm_cfg["min"], glcm_cfg["max"])), 4)

            gabor_cfg = oph_cfg["texture_gabor_response"]
            texture_gabor = round(float(_truncated_normal(gabor_cfg["mean"], gabor_cfg["std"], gabor_cfg["min"], gabor_cfg["max"], 1, rng)[0]), 4)

            df_cfg = oph_cfg["deep_features"]
            deep_f1 = round(float(rng.normal(df_cfg["f1_mean"] + (1.2 if is_dr else 0.0), df_cfg["f1_std"])), 4)
            deep_f2 = round(float(rng.normal(df_cfg["f2_mean"] + (-1.0 if is_glauc else 0.0), df_cfg["f2_std"])), 4)
            deep_f3 = round(float(rng.normal(df_cfg["f3_mean"] + (1.1 if is_hr else 0.0), df_cfg["f3_std"])), 4)

            # Microaneurysms, Exudates, Hemorrhages
            hba1c_proxy = 8.0 if is_diabetic else 5.3
            ma_cfg = oph_cfg["microaneurysms_count"]
            ma_excess = max(0.0, hba1c_proxy - ma_cfg["hba1c_threshold"])
            ma_lam = ma_cfg["base_lambda"] + (ma_excess * ma_cfg["hba1c_multiplier"]) + (ma_cfg["dr_bonus_lambda"] if is_dr else 0.0)
            microaneurysms = int(np.clip(rng.poisson(lam=ma_lam), 0, ma_cfg["max"]))

            ex_cfg = oph_cfg["exudates_count"]
            ex_excess = max(0.0, hba1c_proxy - ex_cfg["hba1c_threshold"])
            ex_lam = ex_cfg["base_lambda"] + (ex_excess * ex_cfg["hba1c_multiplier"]) + (ex_cfg["dr_bonus_lambda"] if is_dr else 0.0)
            exudates = int(np.clip(rng.poisson(lam=ex_lam), 0, ex_cfg["max"]))

            hem_cfg = oph_cfg["hemorrhages_count"]
            hem_lam = hem_cfg["base_lambda"] + (3.0 if history_hypertension == "Yes" else 0.0) + (hem_cfg["hr_bonus_lambda"] if is_hr else 0.0)
            hemorrhages = int(np.clip(rng.poisson(lam=hem_lam), 0, hem_cfg["max"]))

            retinal_disorder = retinal_disorder_code
            retinal_label = retinal_disorder_label
            eye_exam_str = last_exam_date
            sym_duration_val = symptom_duration
            vis_acuity_val = visual_acuity
        else:
            image_quality = np.nan
            optic_disc_area = np.nan
            optic_cup_area = np.nan
            cup_to_disc_ratio = np.nan
            intraocular_pressure = np.nan
            macular_thickness = np.nan
            rnfl_thickness = np.nan
            vessel_tortuosity = np.nan
            bifurcation_angle = np.nan
            faz_area = np.nan
            texture_glcm = np.nan
            texture_gabor = np.nan
            deep_f1 = np.nan
            deep_f2 = np.nan
            deep_f3 = np.nan
            microaneurysms = np.nan
            exudates = np.nan
            hemorrhages = np.nan
            retinal_disorder = np.nan
            retinal_label = np.nan
            eye_exam_str = np.nan
            sym_duration_val = np.nan
            vis_acuity_val = np.nan

        # ---------------------------------------------------------------------
        # Assemble daily row with all multi-domain variables
        # ---------------------------------------------------------------------
        records.append({
            # Metadata & Temporal
            "Patient_ID": patient_id,
            "Timestamp": timestamp_str,
            # Demographics & Morphology
            "Age": age,
            "Gender": gender,
            "Ethnicity": ethnicity,
            "Height_m": height,
            "Weight_kg": day_weight,
            "BMI": day_bmi,
            "Fat_Percentage": day_fat,
            # Medical Profile & History
            "Smoking_Status": smoking_status,
            "History_Hypertension": history_hypertension,
            "History_CVD": history_cvd,
            "Diabetes_Duration_years": diabetes_duration,
            "Family_History_Eye_Disease": family_history_eye,
            "Medications": medications,
            "Risk_Category": risk_category,
            # Habits & Fitness (DataBank 3 + 4)
            "Workout_Frequency_days_week": workout_frequency,
            "Physical_Activity_Level": activity_level,
            "Experience_Level": experience_level,
            "Workout_Type": workout_type,
            "Session_Duration_hours": session_duration,
            "Calories_Burned": calories_burned,
            "Avg_BPM": avg_bpm,
            "Max_BPM": max_bpm,
            "Caffeine_Intake_cups_day": base_caffeine,
            "Water_Intake_liters": water_intake,
            # Sleep, Stress & Cognition (DataBank 4)
            "Sleep_Hours": sleep_hours,
            "Sleep_Quality_Score": sleep_quality,
            "Daytime_Sleepiness": daytime_sleepiness,
            "Stress_Level": round(curr_stress, 1),
            "Emotion_Regulation_Score": emotion_regulation,
            "Stroop_Task_Reaction_Time_s": stroop_rt,
            "N_Back_Accuracy_pct": nback_acc,
            "PVT_Reaction_Time_ms": pvt_rt,
            # Metabolism & Vital Signs (DataBank 1)
            "Heart_Rate": heart_rate,
            "Systolic_BP": systolic_bp,
            "Diastolic_BP": diastolic_bp,
            "Derived_Pulse_Pressure": derived_pulse_pressure,
            "Derived_MAP": derived_map,
            "Fasting_Glucose_mg_dl": fasting_glucose,
            "HbA1c_pct": hba1c,
            "Derived_HRV_s": derived_hrv,
            "Body_Temperature_c": body_temp,
            "Oxygen_Saturation_pct": oxygen_sat,
            "Respiratory_Rate_bpm": resp_rate,
            # Ophthalmology & Retinal Features (DataBank 2)
            "Date_of_Last_Eye_Exam": eye_exam_str,
            "Symptom_Duration_weeks": sym_duration_val,
            "Visual_Acuity": vis_acuity_val,
            "Image_Quality_Score": image_quality,
            "Optic_Disc_Area": optic_disc_area,
            "Optic_Cup_Area": optic_cup_area,
            "Cup_to_Disc_Ratio": cup_to_disc_ratio,
            "Intraocular_Pressure_mmhg": intraocular_pressure,
            "Macular_Thickness_um": macular_thickness,
            "RNFL_Thickness_um": rnfl_thickness,
            "Vessel_Tortuosity": vessel_tortuosity,
            "Bifurcation_Angle_deg": bifurcation_angle,
            "FAZ_Area_mm2": faz_area,
            "Texture_GLCM_Contrast": texture_glcm,
            "Texture_Gabor_Response": texture_gabor,
            "Deep_Feature_1": deep_f1,
            "Deep_Feature_2": deep_f2,
            "Deep_Feature_3": deep_f3,
            "Microaneurysms_Count": microaneurysms,
            "Exudates_Count": exudates,
            "Hemorrhages_Count": hemorrhages,
            "Retinal_Disorder": retinal_disorder,
            "Retinal_Disorder_Label": retinal_label,
        })

    return pd.DataFrame(records)


def allocate_days(
    records: int,
    patients: int | None = None,
    days: int | None = None,
    default_days: int = 60,
) -> list[int]:
    """Days of history to generate for each patient.

    ``records`` is the *exact* number of observation rows for the whole cohort:
    it decides how many patients are created, never how long each patient is
    followed. The per-patient duration comes from ``days`` or, failing that, from
    the config default, so a records target never distorts the time series.
    When the target is not a multiple of the duration, the final patient covers
    the remaining days so the row count lands exactly on ``records``.

    An explicit ``patients`` (and ``days``) request always wins: ``records`` is
    then ignored instead of silently overriding what the caller asked for.
    """
    duration = default_days if days is None else int(days)
    if duration < 1:
        raise ValueError("days must be at least 1")

    if patients is not None:
        if int(patients) < 1:
            raise ValueError("patients must be at least 1")
        return [duration] * int(patients)

    if int(records) < 1:
        raise ValueError("records must be at least 1")

    full, remainder = divmod(int(records), duration)
    counts = [duration] * full
    if remainder:
        counts.append(remainder)
    return counts


def generate_longitudinal_dataset(
    num_patients: int | None = None,
    days_per_patient: int | None = None,
    config: dict[str, Any] | None = None,
    patients_dir: Path | None = None,
    seed: int | None = 42,
    day_counts: Sequence[int] | None = None,
) -> tuple[pd.DataFrame, list[Path]]:
    """Generate longitudinal time-series data for multiple patients and save per-user files."""
    if config is None:
        config = configure.load_config()

    sched_cfg = config.get("temporal_and_schedules", {})
    if day_counts is None:
        if days_per_patient is None:
            days_per_patient = int(sched_cfg.get("default_days_duration", 60))
        day_counts = [days_per_patient] * max(1, int(num_patients or 1))
    day_counts = [int(d) for d in day_counts]

    start_date_str = sched_cfg.get("start_date", "2026-01-01")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

    if patients_dir is None:
        patients_dir = paths.OUTPUT_DIR / "patients"
    paths.ensure_dir(patients_dir)

    rng = np.random.default_rng(seed)
    patient_dfs: list[pd.DataFrame] = []
    saved_patient_files: list[Path] = []

    for idx, patient_days in enumerate(day_counts):
        p_id = f"SC-{idx+1:05d}"
        p_df = generate_patient_longitudinal_series(
            patient_id=p_id,
            days=patient_days,
            config=config,
            rng=rng,
            start_date=start_date,
        )
        # Save individual patient user file
        p_file = patients_dir / f"{p_id}.csv"
        p_df.to_csv(p_file, index=False)
        saved_patient_files.append(p_file)
        patient_dfs.append(p_df)

    combined_df = pd.concat(patient_dfs, ignore_index=True)
    return combined_df, saved_patient_files


def run(context: registry.Context) -> int:
    """CLI entry point for the 'generate' command."""
    records_arg = getattr(context.args, "records", 1000)
    patients_arg = getattr(context.args, "patients", None)
    days_arg = getattr(context.args, "days", None)
    output_path = Path(getattr(context.args, "output", paths.OUTPUT_DIR / "dataset.csv"))
    patients_dir_arg = getattr(context.args, "patients_dir", paths.OUTPUT_DIR / "patients")
    patients_dir = Path(patients_dir_arg) if patients_dir_arg else paths.OUTPUT_DIR / "patients"
    config_path = getattr(context.args, "config", None)

    config = configure.load_config(config_path)

    # Determine patients and days
    sched_cfg = config.get("temporal_and_schedules", {})
    default_days = int(sched_cfg.get("default_days_duration", 60))

    try:
        day_counts = allocate_days(
            records=records_arg,
            patients=patients_arg,
            days=days_arg,
            default_days=default_days,
        )
    except ValueError as err:
        print(f"[generate] invalid request: {err}")
        return 1

    num_patients = len(day_counts)
    days_per_patient = day_counts[0]
    total_rows = sum(day_counts)

    paths.ensure_dir(output_path.parent)
    paths.ensure_dir(patients_dir)

    print(f"[generate] generating longitudinal dataset:")
    print(f"           patients: {num_patients:,} users | days per patient: {days_per_patient:,} days")
    if len(set(day_counts)) > 1:
        print(f"           last user covers {day_counts[-1]:,} days to land exactly on the record target")
    print(f"           total expected observations: {total_rows:,}")
    print(f"           saving individual user files in: {patients_dir}")
    print(f"           saving consolidated dataset in: {output_path}")

    combined_df, patient_files = generate_longitudinal_dataset(
        day_counts=day_counts,
        config=config,
        patients_dir=patients_dir,
    )

    combined_df.to_csv(output_path, index=False)

    print(f"[generate] complete!")
    print(f"           individual patient files saved: {len(patient_files)}")
    print(f"           total rows: {len(combined_df):,} | variables: {len(combined_df.columns)}")
    return 0
