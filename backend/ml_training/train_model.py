"""
Train the Random Forest tutor-match model on the included SYNTHETIC dataset.

Run from the backend folder:
    python ml_training/train_model.py

IMPORTANT: labels were produced by a documented heuristic (subject 40%,
expertise 25%, preference 20%, availability 15%, plus small noise), NOT by real
tutoring outcomes. Metrics measure agreement with those synthetic labels only.

Same data, features, feature order, 80/20 stratified split, random seed (42) and
hyper-parameters as the originally supplied training script. Additions: dataset
validation, a check that the CSV's derived features equal what the backend's
feature code (app/ml/features.py) produces, and version metadata in the artifact.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score)
from sklearn.model_selection import train_test_split

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
from app.ml import features as feat  # noqa: E402  (shared feature definitions)

DATA_PATH = Path(__file__).resolve().parent / "data" / "tutor_matching_dataset.csv"
ARTIFACT_DIR = BACKEND_DIR / "app" / "ml" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "tutor_match_model.joblib"
METRICS_PATH = ARTIFACT_DIR / "evaluation_metrics.json"

FEATURES = feat.FEATURE_ORDER
RANDOM_SEED = 42
TEST_SIZE = 0.20
HYPERPARAMETERS = dict(n_estimators=200, max_depth=8, min_samples_leaf=3,
                       class_weight="balanced", random_state=RANDOM_SEED)
RAW_COLUMNS = ["learner_subject", "tutor_subjects", "learner_learning_preference",
               "tutor_learning_preference", "learner_availability", "tutor_availability"]


def validate_dataset(df: pd.DataFrame) -> None:
    """Fail loudly on schema/value problems and on training/inference definition drift."""
    missing = [c for c in FEATURES + ["match_label"] + RAW_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")
    if df[FEATURES + ["match_label"]].isna().any().any():
        raise ValueError("Dataset has missing values in feature/label columns.")
    if not set(df["match_label"].unique()) <= {0, 1}:
        raise ValueError("match_label must be 0/1.")
    for col in ("subject_match", "preference_match", "availability_match"):
        if not set(df[col].unique()) <= {0, 1}:
            raise ValueError(f"{col} must be 0/1.")
    if not df["tutor_expertise_1_to_5"].between(1, 5).all():
        raise ValueError("tutor_expertise_1_to_5 must be within 1-5.")

    # The CSV's pre-computed features must equal the backend's feature functions.
    recomputed = pd.DataFrame({
        "subject_match": [feat.subject_match([r.learner_subject], r.tutor_subjects.split("|"))
                          for r in df.itertuples()],
        "preference_match": [feat.preference_match(r.learner_learning_preference, r.tutor_learning_preference)
                             for r in df.itertuples()],
        "availability_match": [feat.availability_match([r.learner_availability], [r.tutor_availability])
                               for r in df.itertuples()],
    })
    for col in recomputed.columns:
        if not (recomputed[col].values == df[col].values).all():
            raise ValueError(f"Feature '{col}' in the CSV disagrees with app/ml/features.py.")


def main() -> dict:
    df = pd.read_csv(DATA_PATH)
    validate_dataset(df)
    print(f"Dataset OK: {len(df)} rows, {int(df.duplicated().sum())} exact duplicate rows, "
          f"label balance {df['match_label'].value_counts().to_dict()}")

    X, y = df[FEATURES], df["match_label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y)

    model = RandomForestClassifier(**HYPERPARAMETERS)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "dataset_type": "synthetic",
        "rows_total": int(len(df)),
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(X_test)),
        "features": FEATURES,
        "algorithm": "RandomForestClassifier",
        "hyperparameters": HYPERPARAMETERS,
        "random_seed": RANDOM_SEED,
        "test_size": TEST_SIZE,
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "confusion_matrix_labels_0_1": confusion_matrix(y_test, predictions, labels=[0, 1]).tolist(),
        "feature_importances": {f: round(float(v), 4) for f, v in zip(FEATURES, model.feature_importances_)},
        "class_0_is": "not a match according to synthetic labeling rule",
        "class_1_is": "match according to synthetic labeling rule",
        "dataset_sha256": hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
        "sklearn_version": sklearn.__version__,
        "pandas_version": pd.__version__,
        "python_version": platform.python_version(),
        "warning": "These metrics do not establish real-world tutor-matching performance because the labels are synthetic.",
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "sklearn_version": sklearn.__version__,
                 "dataset_sha256": metrics["dataset_sha256"]}, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    print("\nClassification report (synthetic labels):")
    print(classification_report(y_test, predictions, zero_division=0))
    print(f"Saved model to:   {MODEL_PATH}")
    print(f"Saved metrics to: {METRICS_PATH}")
    return metrics


if __name__ == "__main__":
    main()
