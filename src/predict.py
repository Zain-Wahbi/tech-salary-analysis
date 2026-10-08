"""Predict an annual tech salary (USD) with an 80% range from a respondent profile.

Run from the repository root:

    python -m src.predict --country "United States" --experience 8 --role "Developer, back-end" --education "Bachelor's degree" --remote "Remote" --languages "Python;SQL;JavaScript"

The model is trained and saved by notebooks/06_salary_regression_model.ipynb.
Category values must match the survey wording used in the notebooks.
"""
import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.features import build_features

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "salary_model.joblib"


def load_artifact(path=MODEL_PATH):
    """Load the trained pipeline and the metadata saved by the training notebook."""
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Model not found at {path}. Run notebooks/06_salary_regression_model.ipynb first."
        )
    return joblib.load(path)


def predict_salary(profile, artifact=None):
    """Return the predicted salary and its 80% range for one respondent profile (a dict)."""
    artifact = artifact or load_artifact()

    row = pd.DataFrame([{
        "WorkExp": profile["experience"],
        "Country": profile["country"],
        "DevType": profile["role"],
        "EdLevel": profile["education"],
        "RemoteWork": profile["remote"],
        "OrgSize": profile.get("org_size"),
        "Age": profile.get("age"),
        "Employment": profile.get("employment"),
        "LanguageHaveWorkedWith": profile.get("languages"),
    }])
    features = build_features(row, artifact["top_languages"])
    predicted_log = float(artifact["pipeline"].predict(features)[0])

    # Countries with enough respondents have their own range; the others share a wider one
    ranges = artifact["residual_quantiles_log"]
    bounds = ranges["by_country"].get(profile["country"], ranges["smaller_countries"])

    return {
        "prediction": float(np.exp(predicted_log)),
        "low": float(np.exp(predicted_log + bounds["p10"])),
        "high": float(np.exp(predicted_log + bounds["p90"])),
        "own_country_range": profile["country"] in ranges["by_country"],
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Predict an annual tech salary (USD) with an 80% range."
    )
    parser.add_argument("--country", required=True, help='Country as in the survey, e.g. "United States"')
    parser.add_argument("--experience", type=float, required=True, help="Years of professional experience")
    parser.add_argument("--role", required=True, help='Job role, e.g. "Developer, back-end"')
    parser.add_argument("--education", required=True, help='Education, e.g. "Bachelor\'s degree"')
    parser.add_argument("--remote", required=True, help='Work arrangement, e.g. "Remote" or "In-person"')
    parser.add_argument("--org-size", default=None, help="Company size as in the survey (optional)")
    parser.add_argument("--age", default=None, help='Age group, e.g. "25-34 years old" (optional)')
    parser.add_argument("--employment", default="Employed",
                        help='"Employed" or "Independent contractor, freelancer, or self-employed"')
    parser.add_argument("--languages", default="", help='Languages separated by ";", e.g. "Python;SQL"')
    return parser.parse_args()


def main():
    args = parse_args()
    profile = {
        "country": args.country,
        "experience": args.experience,
        "role": args.role,
        "education": args.education,
        "remote": args.remote,
        "org_size": args.org_size,
        "age": args.age,
        "employment": args.employment,
        "languages": args.languages,
    }
    try:
        result = predict_salary(profile)
    except FileNotFoundError as error:
        raise SystemExit(f"Error: {error}")
    print(f"Predicted salary: ${round(result['prediction'], -2):,.0f}")
    print(f"80% range:        ${round(result['low'], -2):,.0f} to ${round(result['high'], -2):,.0f}")
    if not result["own_country_range"]:
        print("Note: few respondents come from this country, so a wider shared range is used.")


if __name__ == "__main__":
    main()