"""
Loads the trained model ONCE and caches it (including a failed load, so a broken
artifact does not get re-read on every request).

Failures raise ModelUnavailableError with a clear message; the recommendation
service then falls back to the heuristic scorer and labels the results as such.
"""
from __future__ import annotations

import logging
import threading
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import sklearn

from app.ml.features import FEATURE_ORDER

logger = logging.getLogger(__name__)

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "tutor_match_model.joblib"
METRICS_PATH = ARTIFACT_DIR / "evaluation_metrics.json"


class ModelUnavailableError(RuntimeError):
    """The ML model could not be loaded or is not usable."""


_lock = threading.Lock()
_bundle: Optional[Dict[str, Any]] = None
_error: Optional[str] = None


def load_model_bundle(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and validate the model artifact (uncached). Raises ModelUnavailableError."""
    path = Path(path) if path is not None else Path(MODEL_PATH)
    if not path.is_file():
        raise ModelUnavailableError(
            f"Model file not found at {path}. Run `python ml_training/train_model.py` from the backend folder."
        )
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # version mismatch is checked explicitly below
            bundle = joblib.load(path)
    except Exception as exc:  # corrupt file, incompatible pickle, missing dependency...
        raise ModelUnavailableError(f"Could not load model file {path.name}: {exc}") from exc

    if not isinstance(bundle, dict) or "model" not in bundle or "features" not in bundle:
        raise ModelUnavailableError("Model file has an unexpected format (expected keys 'model' and 'features').")
    if list(bundle["features"]) != FEATURE_ORDER:
        raise ModelUnavailableError(
            f"Model feature order {list(bundle['features'])} does not match the backend's {FEATURE_ORDER}."
        )
    model = bundle["model"]
    if not hasattr(model, "predict_proba") or 1 not in list(getattr(model, "classes_", [])):
        raise ModelUnavailableError("Model does not provide probabilities for class 1 (match).")

    trained_with = bundle.get("sklearn_version")
    if trained_with and trained_with != sklearn.__version__:
        raise ModelUnavailableError(
            f"Model was trained with scikit-learn {trained_with} but {sklearn.__version__} is installed. "
            "Install the pinned requirements or retrain with `python ml_training/train_model.py`."
        )
    return bundle


def get_model_bundle() -> Dict[str, Any]:
    """Return the cached model bundle, loading it on first use."""
    global _bundle, _error
    with _lock:
        if _bundle is not None:
            return _bundle
        if _error is not None:
            raise ModelUnavailableError(_error)
        try:
            _bundle = load_model_bundle()
            logger.info("Tutor-match model loaded from %s", MODEL_PATH)
            return _bundle
        except ModelUnavailableError as exc:
            _error = str(exc)
            logger.error("Tutor-match model unavailable: %s", exc)
            raise


def reset_model_cache() -> None:
    """Forget the cached model/error (used by tests and after retraining)."""
    global _bundle, _error
    with _lock:
        _bundle = None
        _error = None
