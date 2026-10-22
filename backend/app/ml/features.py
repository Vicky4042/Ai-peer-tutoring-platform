"""
Feature derivation for the tutor-match Random Forest.

This module is the SINGLE source of truth for how the four model features
are defined. Both the training script (ml_training/train_model.py) and the
backend prediction path import it, so training and inference cannot drift.

Model features (order matters and must never change without retraining):
    1. subject_match            1 if ANY subject the learner requested is taught by the tutor
    2. tutor_expertise_1_to_5   tutor expertise level, integer 1-5
    3. preference_match         1 if learner/tutor learning styles match after mapping
                                to the model's training categories, else 0
    4. availability_match       1 if learner and tutor share AT LEAST ONE slot, else 0

ASSUMPTIONS (not validated against real learners, see README):
  * The app's learning-style options differ from the dataset's categories, so
    they are mapped:  Visual->Visual, Auditory->Discussion,
    Kinesthetic->Practical, Reading/Writing->Reading.
  * The dataset has one availability slot per person (Morning/Afternoon/Evening).
    The app allows several slots, including Weekend. "At least one shared slot"
    extends the dataset's definition beyond what the model was trained on.
  * The dataset has exactly one requested subject per learner. The app allows
    several, so "any requested subject taught by the tutor" is used.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Optional

FEATURE_ORDER = [
    "subject_match",
    "tutor_expertise_1_to_5",
    "preference_match",
    "availability_match",
]

# App preference label (normalised) -> model training category.
# The three non-identity mappings are ASSUMPTIONS. The model's own categories
# are also accepted unchanged so data in the dataset vocabulary still works.
PREFERENCE_TO_MODEL_CATEGORY = {
    "visual": "Visual",
    "auditory": "Discussion",
    "kinesthetic": "Practical",
    "reading/writing": "Reading",
    "reading": "Reading",
    "discussion": "Discussion",
    "practical": "Practical",
}


class InvalidProfileError(ValueError):
    """Raised when a profile value cannot be turned into a valid model feature."""


def normalize_text(value: Any) -> str:
    """Lower-case, trim and collapse internal whitespace. None -> ''."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def normalize_set(values: Any) -> set:
    """Normalised set from a list of strings. None/empty/blank entries are ignored.
    A bare string is treated as a single value (not iterated character by character)."""
    if values is None:
        return set()
    if isinstance(values, str):
        values = [values]
    try:
        items: Iterable = iter(values)
    except TypeError:
        return set()
    return {n for n in (normalize_text(v) for v in items) if n}


def map_preference(value: Any) -> Optional[str]:
    """Map an app learning-style label to the model's training category.
    Returns None for missing or unknown values (treated as 'no match')."""
    key = normalize_text(value)
    key = re.sub(r"\s*/\s*", "/", key)  # 'Reading / Writing' -> 'reading/writing'
    return PREFERENCE_TO_MODEL_CATEGORY.get(key)


def subject_match(learner_subjects: Any, tutor_subjects: Any) -> int:
    """1 if the learner requested at least one subject the tutor teaches (exact, case-insensitive)."""
    return int(bool(normalize_set(learner_subjects) & normalize_set(tutor_subjects)))


def preference_match(learner_preference: Any, tutor_preference: Any) -> int:
    lp = map_preference(learner_preference)
    tp = map_preference(tutor_preference)
    return int(lp is not None and lp == tp)


def availability_match(learner_slots: Any, tutor_slots: Any) -> int:
    """1 if at least one slot is shared (case-insensitive)."""
    return int(bool(normalize_set(learner_slots) & normalize_set(tutor_slots)))


def parse_expertise(value: Any) -> int:
    """Validate expertise as an integer 1-5. Raises InvalidProfileError otherwise."""
    if value is None or isinstance(value, bool):
        raise InvalidProfileError(f"Invalid expertise level: {value!r}")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise InvalidProfileError(f"Invalid expertise level: {value!r}") from None
    if number != number or number != int(number):  # NaN or non-integral
        raise InvalidProfileError(f"Invalid expertise level: {value!r}")
    level = int(number)
    if not 1 <= level <= 5:
        raise InvalidProfileError(f"Expertise level must be 1-5, got {level}")
    return level


def teaches_requested_subject(learner: Dict[str, Any], tutor: Dict[str, Any]) -> bool:
    """Eligibility rule used by BOTH ML and fallback ranking."""
    return bool(subject_match(learner.get("subjects"), tutor.get("subjects")))


def build_features(learner: Dict[str, Any], tutor: Dict[str, Any]) -> Dict[str, int]:
    """
    Derive the four model features from a learner dict and a tutor dict.

    learner keys: subjects (list[str]), learning_preference (str), availability (list[str])
    tutor keys:   subjects (list[str]), expertise_level (int 1-5),
                  teaching_preference (str), availability (list[str])

    Missing preference/availability/subjects yield 0 for that feature (unknown
    cannot match). Invalid expertise raises InvalidProfileError.
    """
    return {
        "subject_match": subject_match(learner.get("subjects"), tutor.get("subjects")),
        "tutor_expertise_1_to_5": parse_expertise(tutor.get("expertise_level")),
        "preference_match": preference_match(
            learner.get("learning_preference"), tutor.get("teaching_preference")
        ),
        "availability_match": availability_match(
            learner.get("availability"), tutor.get("availability")
        ),
    }
