"""Feature engineering shared by the training notebook and the prediction script.

The code mirrors notebooks/06_salary_regression_model.ipynb. It uses no statistic
computed from the data, so it can be applied safely to a single new respondent.
"""
import re

import numpy as np
import pandas as pd

NUM_COLS = ["WorkExp"]
CAT_COLS = ["Country", "DevType", "EdGroup", "RemoteWork", "OrgSize", "Age", "Employment"]


def simplify_education(text):
    """Map the long survey answers to a few readable groups."""
    if pd.isna(text):
        return np.nan
    t = text.lower()
    if "professional degree" in t or "ph.d" in t or "doctorate" in t:
        return "Doctorate / professional"
    if "master" in t:
        return "Master's"
    if "bachelor" in t:
        return "Bachelor's"
    if "associate" in t:
        return "Associate"
    if "some college" in t:
        return "Some college"
    if "secondary" in t:
        return "Secondary school"
    if "primary" in t:
        return "Primary school"
    return "Other"


def clean_name(lang):
    """Make a safe column name (C++ and C# must not collide with C)."""
    return re.sub(r"\W+", "_", lang.replace("+", "plus").replace("#", "sharp")).strip("_")


def build_features(frame, language_list):
    """Turn raw survey rows into model features. Uses no statistic computed from the data."""
    X = pd.DataFrame(index=frame.index)
    X["WorkExp"] = pd.to_numeric(frame["WorkExp"], errors="coerce")
    X["Country"] = frame["Country"]
    X["DevType"] = frame["DevType"]
    X["EdGroup"] = frame["EdLevel"].apply(simplify_education)
    X["RemoteWork"] = frame["RemoteWork"]
    X["OrgSize"] = frame["OrgSize"]
    X["Age"] = frame["Age"]
    X["Employment"] = frame["Employment"]

    # Missing categories become their own level (a constant, so no leakage)
    for col in CAT_COLS:
        X[col] = X[col].fillna("Missing").astype(object)

    # Multi-select languages become one 0/1 flag per language
    lang_sets = frame["LanguageHaveWorkedWith"].apply(
        lambda s: {x.strip() for x in s.split(";")} if isinstance(s, str) else set()
    )
    for lang in language_list:
        X[f"Lang_{clean_name(lang)}"] = lang_sets.apply(lambda s, l=lang: int(l in s))
    return X