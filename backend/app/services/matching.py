"""
Compatibility-based matching service — Review-2 implementation.

IMPORTANT (academic honesty): this is a deterministic, weighted
compatibility-scoring function, NOT a trained machine-learning model.
It is intentionally simple so it can be explained clearly during the
Review-2 viva. A more advanced ML/recommendation approach is planned
for the final review (see README "Future Work").

Weights (must sum to 1.0):
    subject/skill compatibility ......... 40%
    tutor expertise ..................... 25%
    learning preference match ........... 20%
    availability overlap ................ 15%
"""

from typing import Iterable

WEIGHTS = {
    "subject": 0.40,
    "expertise": 0.25,
    "preference": 0.20,
    "availability": 0.15,
}

# Partial credit when learner's preference and tutor's teaching style
# don't match exactly but aren't unrelated either. Kept simple and
# explicit on purpose.
PARTIAL_PREFERENCE_CREDIT = 40.0


def _normalize(values: Iterable[str]) -> set:
    """Lower-case and strip a list of strings for case-insensitive comparison."""
    return {str(v).strip().lower() for v in values if str(v).strip()}


def subject_overlap_score(learner_subjects: Iterable[str], tutor_subjects: Iterable[str]) -> float:
    """
    Jaccard-style overlap between what the learner needs and what the
    tutor teaches, scaled to 0-100. This rewards tutors who cover the
    learner's required subjects without penalizing them for teaching
    additional subjects outside the learner's list.
    """
    learner_set = _normalize(learner_subjects)
    tutor_set = _normalize(tutor_subjects)
    if not learner_set:
        return 0.0
    matched = learner_set & tutor_set
    # Scored against the learner's requirement set, not the union,
    # so a tutor covering every subject the learner needs scores 100
    # even if the tutor also teaches unrelated subjects.
    return round((len(matched) / len(learner_set)) * 100, 2)


def expertise_score(tutor_expertise_level: int) -> float:
    """
    Tutor expertise level is stored as an integer 1-5
    (1 = beginner-friendly tutor, 5 = highly experienced).
    Scaled linearly to 0-100.
    """
    level = max(0, min(5, int(tutor_expertise_level or 0)))
    return round((level / 5) * 100, 2)


def preference_score(learner_preference: str, tutor_preference: str) -> float:
    """
    Exact match on learning/teaching style scores 100.
    Any non-empty mismatch gets partial credit rather than zero,
    since a preference mismatch alone should not disqualify an
    otherwise well-matched tutor.
    """
    lp = (learner_preference or "").strip().lower()
    tp = (tutor_preference or "").strip().lower()
    if not lp or not tp:
        return 0.0
    if lp == tp:
        return 100.0
    return PARTIAL_PREFERENCE_CREDIT


def availability_overlap_score(learner_slots: Iterable[str], tutor_slots: Iterable[str]) -> float:
    """
    Overlap between learner's available time slots (e.g. 'Morning',
    'Evening', 'Weekend') and the tutor's available slots, scaled to
    0-100 against the learner's requested slots.
    """
    learner_set = _normalize(learner_slots)
    tutor_set = _normalize(tutor_slots)
    if not learner_set:
        return 0.0
    matched = learner_set & tutor_set
    return round((len(matched) / len(learner_set)) * 100, 2)


def compute_compatibility(learner: dict, tutor: dict) -> dict:
    """
    Compute the overall weighted compatibility score (0-100) between a
    learner and a single tutor, along with the per-factor breakdown so
    the UI/backend can show why a tutor was ranked where it was.

    Expected `learner` keys: subjects (list[str]), learning_preference (str),
        availability (list[str])
    Expected `tutor` keys: subjects (list[str]), expertise_level (int 1-5),
        teaching_preference (str), availability (list[str])
    """
    s_score = subject_overlap_score(learner.get("subjects", []), tutor.get("subjects", []))
    e_score = expertise_score(tutor.get("expertise_level", 0))
    p_score = preference_score(learner.get("learning_preference", ""), tutor.get("teaching_preference", ""))
    a_score = availability_overlap_score(learner.get("availability", []), tutor.get("availability", []))

    total = (
        s_score * WEIGHTS["subject"]
        + e_score * WEIGHTS["expertise"]
        + p_score * WEIGHTS["preference"]
        + a_score * WEIGHTS["availability"]
    )

    return {
        "compatibility_score": round(total, 2),
        "breakdown": {
            "subject_score": s_score,
            "expertise_score": e_score,
            "preference_score": p_score,
            "availability_score": a_score,
        },
    }


def rank_tutors(learner: dict, tutors: list) -> list:
    """
    Score every candidate tutor against the learner and return them
    sorted by compatibility_score, highest first. Each returned dict
    is the original tutor record plus its score/breakdown attached.
    """
    ranked = []
    for tutor in tutors:
        result = compute_compatibility(learner, tutor)
        ranked.append({**tutor, **result})
    ranked.sort(key=lambda t: t["compatibility_score"], reverse=True)
    return ranked
