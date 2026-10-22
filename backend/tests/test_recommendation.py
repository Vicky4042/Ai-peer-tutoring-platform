"""Subject filtering, ML ranking, expertise tiebreak and fallback behaviour."""
import pytest

from app.ml import model_loader
from app.services.recommendation import recommend_tutors


@pytest.fixture(autouse=True)
def _fresh_cache(monkeypatch):
    monkeypatch.delenv("MATCHING_MODE", raising=False)
    model_loader.reset_model_cache()
    yield
    model_loader.reset_model_cache()


LEARNER = {"subjects": ["Java", "DSA"], "learning_preference": "Visual", "availability": ["Evening"]}


def tutor(tid, name, subjects, expertise, pref, avail):
    return {"tutor_id": tid, "name": name, "subjects": subjects, "expertise_level": expertise,
            "teaching_preference": pref, "availability": avail}


# Same five demo tutors as seed_data.py
SEED_TUTORS = [
    tutor(1, "Rahul", ["Java", "DSA"], 4, "Visual", ["Evening"]),
    tutor(2, "Priya", ["Python", "SQL"], 5, "Reading/Writing", ["Morning"]),
    tutor(3, "Karthik", ["Java"], 3, "Visual", ["Evening", "Weekend"]),
    tutor(4, "Sneha", ["DSA", "C++"], 4, "Auditory", ["Morning", "Evening"]),
    tutor(5, "Arjun", ["Web Development"], 2, "Kinesthetic", ["Weekend"]),
]


def test_tutors_without_requested_subject_are_excluded():
    names = [t["name"] for t in recommend_tutors(LEARNER, SEED_TUTORS)]
    assert "Priya" not in names and "Arjun" not in names
    assert set(names) == {"Rahul", "Karthik", "Sneha"}


def test_no_eligible_tutors_returns_empty_list():
    learner = {**LEARNER, "subjects": ["Chemistry"]}
    assert recommend_tutors(learner, SEED_TUTORS) == []


def test_learner_without_subjects_gets_no_recommendations():
    assert recommend_tutors({**LEARNER, "subjects": []}, SEED_TUTORS) == []


def test_ml_ranking_fields_and_order():
    ranked = recommend_tutors(LEARNER, SEED_TUTORS)
    assert all(t["scoring_method"] == "ml" for t in ranked)
    assert all(t["fallback_reason"] is None for t in ranked)
    probs = [t["ml_match_probability"] for t in ranked]
    assert all(0.0 <= p <= 1.0 for p in probs)
    assert probs == sorted(probs, reverse=True)
    for t in ranked:  # score shown == probability * 100, so backend and UI agree
        assert t["match_score"] == pytest.approx(t["ml_match_probability"] * 100, abs=0.01)
    # Fully-matched tutors (Rahul, Karthik) must rank above the style-mismatched one (Sneha).
    # NOTE: the order WITHIN the fully-matched group is not asserted: the model saturates near 1.0
    # there (synthetic labels), so differences are tiny and partly label noise.
    assert ranked[-1]["name"] == "Sneha"
    assert {t["name"] for t in ranked[:2]} == {"Rahul", "Karthik"}


def test_better_profile_match_outranks_worse():
    full = tutor(10, "Full", ["Java"], 3, "Visual", ["Evening"])
    none = tutor(11, "SubjectOnly", ["Java"], 3, "Kinesthetic", ["Weekend"])
    ranked = recommend_tutors(LEARNER, [none, full])
    assert [t["name"] for t in ranked] == ["Full", "SubjectOnly"]


def test_preference_mapping_affects_ranking():
    # Learner 'Auditory' maps to Discussion; tutor 'Auditory' maps to Discussion -> match.
    learner = {"subjects": ["Java"], "learning_preference": "Auditory", "availability": ["Evening"]}
    same = tutor(1, "SameStyle", ["Java"], 3, "Auditory", ["Evening"])
    diff = tutor(2, "DiffStyle", ["Java"], 3, "Visual", ["Evening"])
    ranked = recommend_tutors(learner, [diff, same])
    assert ranked[0]["name"] == "SameStyle"
    assert ranked[0]["ml_match_probability"] > ranked[1]["ml_match_probability"]


def test_expertise_breaks_ties_only():
    a = tutor(1, "LowExp", ["Java"], 2, "Visual", ["Evening"])
    b = tutor(2, "HighExp", ["Java"], 5, "Visual", ["Evening"])
    tied = lambda rows: [0.8 for _ in rows]
    ranked = recommend_tutors(LEARNER, [a, b], predict_fn=tied)
    assert [t["name"] for t in ranked] == ["HighExp", "LowExp"]


def test_probability_beats_expertise():
    a = tutor(1, "HighExpLowProb", ["Java"], 5, "Visual", ["Evening"])
    b = tutor(2, "LowExpHighProb", ["Java"], 1, "Visual", ["Evening"])
    ranked = recommend_tutors(LEARNER, [a, b], predict_fn=lambda rows: [0.60, 0.90])
    assert [t["name"] for t in ranked] == ["LowExpHighProb", "HighExpLowProb"]


def test_equal_probability_and_expertise_is_deterministic_by_tutor_id():
    a = tutor(7, "B", ["Java"], 3, "Visual", ["Evening"])
    b = tutor(3, "A", ["Java"], 3, "Visual", ["Evening"])
    ranked = recommend_tutors(LEARNER, [a, b], predict_fn=lambda rows: [0.5, 0.5])
    assert [t["tutor_id"] for t in ranked] == [3, 7]


def test_invalid_expertise_tutor_is_skipped_not_guessed():
    bad = tutor(9, "Bad", ["Java"], 99, "Visual", ["Evening"])
    good = tutor(1, "Good", ["Java"], 3, "Visual", ["Evening"])
    ranked = recommend_tutors(LEARNER, [bad, good])
    assert [t["name"] for t in ranked] == ["Good"]


def test_fallback_when_model_missing_is_labelled(monkeypatch, tmp_path):
    monkeypatch.setattr(model_loader, "MODEL_PATH", tmp_path / "missing.joblib")
    ranked = recommend_tutors(LEARNER, SEED_TUTORS)
    assert ranked, "fallback should still produce recommendations"
    for t in ranked:
        assert t["scoring_method"] == "fallback"
        assert t["ml_match_probability"] is None
        assert "unavailable" in t["fallback_reason"]
        assert t["match_score"] == t["compatibility_score"]
    assert {t["name"] for t in ranked} == {"Rahul", "Karthik", "Sneha"}  # same eligibility filter
    scores = [t["compatibility_score"] for t in ranked]
    assert scores == sorted(scores, reverse=True)


def test_fallback_when_prediction_raises():
    def boom(rows):
        raise RuntimeError("kaboom")
    ranked = recommend_tutors(LEARNER, SEED_TUTORS, predict_fn=boom)
    assert all(t["scoring_method"] == "fallback" and "kaboom" in t["fallback_reason"] for t in ranked)
    assert all(t["ml_match_probability"] is None for t in ranked)


def test_forced_fallback_mode(monkeypatch):
    monkeypatch.setenv("MATCHING_MODE", "fallback")
    ranked = recommend_tutors(LEARNER, SEED_TUTORS)
    assert all(t["scoring_method"] == "fallback" and "MATCHING_MODE" in t["fallback_reason"] for t in ranked)


def test_fallback_scores_match_original_scorer():
    from app.services.matching import compute_compatibility
    ranked = recommend_tutors(LEARNER, SEED_TUTORS, predict_fn=lambda r: (_ for _ in ()).throw(RuntimeError("x")))
    for t in ranked:
        assert t["compatibility_score"] == compute_compatibility(LEARNER, t)["compatibility_score"]
