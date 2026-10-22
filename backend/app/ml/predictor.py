"""Turns derived feature rows into match probabilities using the cached model."""
from __future__ import annotations

from typing import Dict, List

import pandas as pd

from app.ml.features import FEATURE_ORDER
from app.ml.model_loader import get_model_bundle


def predict_match_probabilities(rows: List[Dict[str, int]]) -> List[float]:
    """Probability of class 1 ('match') for each feature row, in input order.
    Raises ModelUnavailableError if the model cannot be loaded."""
    if not rows:
        return []
    bundle = get_model_bundle()
    model = bundle["model"]
    frame = pd.DataFrame(rows, columns=FEATURE_ORDER)  # fixed column order = training order
    class_index = list(model.classes_).index(1)
    return [float(p) for p in model.predict_proba(frame)[:, class_index]]
