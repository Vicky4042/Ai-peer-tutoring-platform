"""
Tutor recommendation orchestration: eligibility filter -> ML ranking -> fallback.

1. Eligibility: only tutors who teach at least one subject the learner requested
   are considered (applies to BOTH ML and fallback ranking).
2. ML ranking: the Random Forest's probability of class 1 ('match') is computed
   from four derived features (app/ml/features.py). Tutors are sorted by that
   probability (rounded to 4 d.p., the precision returned by the API), then by
   tutor expertise as a tiebreaker, then by tutor_id for a deterministic order.
3. Fallback: if the model cannot be loaded or prediction fails (or
   MATCHING_MODE=fallback is set), the original weighted compatibility scorer
   (services/matching.py) is used. Each result says which method produced it:
   scoring_method = "ml" | "fallback"; ml_match_probability is None for fallback.

NOTE: the model was trained on SYNTHETIC labels. Its probabilities are
agreement with a synthetic heuristic, not validated real-world success.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Callable, Dict, List, Optional, Sequence

from app.ml.features import InvalidProfileError, build_features, teaches_requested_subject
from app.ml.model_loader import ModelUnavailableError
from app.ml.predictor import predict_match_probabilities
from app.services.matching import compute_compatibility, rank_tutors

logger = logging.getLogger(__name__)

PredictFn = Callable[[List[Dict[str, int]]], List[float]]


def _forced_fallback_reason() -> Optional[str]:
    if os.getenv("MATCHING_MODE", "ml").strip().lower() == "fallback":
        return "Fallback forced by MATCHING_MODE=fallback"
    return None


def _rank_ml(learner: dict, eligible: Sequence[dict], predict_fn: PredictFn) -> List[dict]:
    scored: List[dict] = []
    rows: List[Dict[str, int]] = []
    for tutor in eligible:
        try:
            rows.append(build_features(learner, tutor))
            scored.append(tutor)
        except InvalidProfileError as exc:
            # Cannot be scored by the model; excluded rather than guessed.
            logger.warning("Skipping tutor %s for ML ranking: %s", tutor.get("tutor_id"), exc)
    if not rows:
        return []

    probabilities = predict_fn(rows)
    if len(probabilities) != len(rows):
        raise RuntimeError("Model returned an unexpected number of predictions.")

    results = []
    for tutor, prob in zip(scored, probabilities):
        prob = round(float(prob), 4)
        results.append({
            **tutor,
            **compute_compatibility(learner, tutor),  # heuristic score + breakdown (reference only)
            "scoring_method": "ml",
            "ml_match_probability": prob,
            "match_score": round(prob * 100, 2),
            "fallback_reason": None,
        })
    results.sort(key=lambda t: (-t["ml_match_probability"],
                                -int(t.get("expertise_level") or 0),
                                t.get("tutor_id") or 0))
    return results


def _rank_fallback(learner: dict, eligible: Sequence[dict], reason: str) -> List[dict]:
    results = []
    for t in rank_tutors(learner, list(eligible)):
        results.append({
            **t,
            "scoring_method": "fallback",
            "ml_match_probability": None,
            "match_score": t["compatibility_score"],
            "fallback_reason": reason,
        })
    return results


def recommend_tutors(learner: dict, tutors: Sequence[dict],
                     predict_fn: Optional[PredictFn] = None) -> List[dict]:
    """Return eligible tutors, best first. `predict_fn` is injectable for tests."""
    eligible = [t for t in tutors if teaches_requested_subject(learner, t)]
    if not eligible:
        return []

    forced = _forced_fallback_reason()
    if forced:
        return _rank_fallback(learner, eligible, forced)

    try:
        return _rank_ml(learner, eligible, predict_fn or predict_match_probabilities)
    except ModelUnavailableError as exc:
        logger.error("ML model unavailable, using fallback scorer: %s", exc)
        return _rank_fallback(learner, eligible, f"ML model unavailable: {exc}")
    except Exception as exc:  # prediction failure must not break the endpoint
        logger.exception("ML prediction failed, using fallback scorer")
        return _rank_fallback(learner, eligible, f"ML prediction failed: {exc}")
