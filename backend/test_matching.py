"""
Standalone sanity tests for app/services/matching.py.
Run with: python3 test_matching.py
No external dependencies required (pure Python).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from services.matching import compute_compatibility, rank_tutors  # noqa: E402


def test_exact_match_scores_high():
    learner = {
        "subjects": ["Java", "DSA"],
        "learning_preference": "Visual",
        "availability": ["Evening"],
    }
    tutor = {
        "name": "Rahul",
        "subjects": ["Java", "DSA", "Python"],
        "expertise_level": 4,
        "teaching_preference": "Visual",
        "availability": ["Evening", "Weekend"],
    }
    result = compute_compatibility(learner, tutor)
    print("Exact-ish match:", result)
    assert result["compatibility_score"] > 80, "Expected a high score for strong overlap"


def test_no_overlap_scores_low():
    learner = {
        "subjects": ["Chemistry"],
        "learning_preference": "Reading/Writing",
        "availability": ["Morning"],
    }
    tutor = {
        "name": "Priya",
        "subjects": ["Python", "SQL"],
        "expertise_level": 2,
        "teaching_preference": "Visual",
        "availability": ["Evening"],
    }
    result = compute_compatibility(learner, tutor)
    print("No overlap:", result)
    assert result["compatibility_score"] < 20, "Expected a low score for no overlap"


def test_ranking_sorts_descending():
    learner = {
        "subjects": ["Java", "DSA"],
        "learning_preference": "Visual",
        "availability": ["Evening"],
    }
    tutors = [
        {"name": "Rahul", "subjects": ["Java", "DSA"], "expertise_level": 4,
         "teaching_preference": "Visual", "availability": ["Evening"]},
        {"name": "Priya", "subjects": ["Python", "SQL"], "expertise_level": 5,
         "teaching_preference": "Reading/Writing", "availability": ["Morning"]},
        {"name": "Karthik", "subjects": ["Java"], "expertise_level": 3,
         "teaching_preference": "Visual", "availability": ["Evening"]},
    ]
    ranked = rank_tutors(learner, tutors)
    scores = [t["compatibility_score"] for t in ranked]
    print("Ranked order:", [(t["name"], t["compatibility_score"]) for t in ranked])
    assert scores == sorted(scores, reverse=True), "Ranked list must be sorted descending"
    assert ranked[0]["name"] == "Rahul", "Rahul should rank first (best overlap on all factors)"


if __name__ == "__main__":
    test_exact_match_scores_high()
    test_no_overlap_scores_low()
    test_ranking_sorts_descending()
    print("\nAll matching tests passed.")
