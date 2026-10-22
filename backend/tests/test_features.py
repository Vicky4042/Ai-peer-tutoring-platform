"""Feature derivation, preference mapping, availability overlap, input safety."""
import pandas as pd
import pytest

from pathlib import Path

from app.ml import features as f

DATASET = Path(__file__).resolve().parent.parent / "ml_training" / "data" / "tutor_matching_dataset.csv"


def test_feature_order_is_fixed():
    assert f.FEATURE_ORDER == ["subject_match", "tutor_expertise_1_to_5",
                               "preference_match", "availability_match"]


@pytest.mark.parametrize("app_value, expected", [
    ("Visual", "Visual"),
    ("Auditory", "Discussion"),
    ("Kinesthetic", "Practical"),
    ("Reading/Writing", "Reading"),
    ("  reading / writing ", "Reading"),
    ("VISUAL", "Visual"),
    ("Discussion", "Discussion"),   # model vocabulary passes through
    ("Practical", "Practical"),
    ("Reading", "Reading"),
    ("Telepathic", None),           # unknown
    ("", None),
    (None, None),
])
def test_preference_mapping(app_value, expected):
    assert f.map_preference(app_value) == expected


def test_preference_match_uses_mapping():
    assert f.preference_match("Auditory", "Discussion") == 1
    assert f.preference_match("Kinesthetic", "Practical") == 1
    assert f.preference_match("Reading/Writing", "Reading") == 1
    assert f.preference_match("Visual", "Auditory") == 0
    assert f.preference_match("Reading/Writing", "Kinesthetic") == 0


def test_unknown_or_missing_preference_never_matches():
    assert f.preference_match("Unknown", "Unknown") == 0
    assert f.preference_match(None, None) == 0
    assert f.preference_match("Visual", "") == 0


def test_availability_overlap_any_shared_slot():
    assert f.availability_match(["Evening"], ["Evening", "Weekend"]) == 1
    assert f.availability_match(["Morning", "Weekend"], ["Weekend"]) == 1   # Weekend supported
    assert f.availability_match(["morning"], ["MORNING"]) == 1              # case-insensitive
    assert f.availability_match(["Morning"], ["Evening"]) == 0
    assert f.availability_match([], ["Evening"]) == 0
    assert f.availability_match(None, ["Evening"]) == 0
    assert f.availability_match(["Evening"], None) == 0


def test_subject_match_any_requested_subject():
    assert f.subject_match(["Java", "DSA"], ["DSA", "C++"]) == 1
    assert f.subject_match(["Java"], ["java "]) == 1
    assert f.subject_match(["Web  Development"], ["web development"]) == 1  # whitespace collapsed
    assert f.subject_match(["Java"], ["Python", "SQL"]) == 0
    assert f.subject_match([], ["Java"]) == 0
    assert f.subject_match(None, ["Java"]) == 0
    assert f.subject_match(["Java"], None) == 0


def test_bare_string_is_not_iterated_per_character():
    assert f.subject_match("Java", ["Java"]) == 1
    assert f.subject_match("a", ["Java"]) == 0


@pytest.mark.parametrize("value, expected", [(1, 1), (5, 5), ("3", 3), (4.0, 4)])
def test_parse_expertise_valid(value, expected):
    assert f.parse_expertise(value) == expected


@pytest.mark.parametrize("value", [None, 0, 6, -1, 2.5, "abc", "", True, float("nan")])
def test_parse_expertise_invalid(value):
    with pytest.raises(f.InvalidProfileError):
        f.parse_expertise(value)


def test_build_features_returns_model_order_and_values():
    learner = {"subjects": ["Java", "DSA"], "learning_preference": "Auditory", "availability": ["Evening"]}
    tutor = {"subjects": ["DSA", "C++"], "expertise_level": 4,
             "teaching_preference": "Discussion", "availability": ["Morning", "Evening"]}
    row = f.build_features(learner, tutor)
    assert list(row.keys()) == f.FEATURE_ORDER
    assert row == {"subject_match": 1, "tutor_expertise_1_to_5": 4,
                   "preference_match": 1, "availability_match": 1}


def test_build_features_handles_missing_profile_fields():
    row = f.build_features({}, {"expertise_level": 3})
    assert row == {"subject_match": 0, "tutor_expertise_1_to_5": 3,
                   "preference_match": 0, "availability_match": 0}


def test_build_features_rejects_invalid_expertise():
    with pytest.raises(f.InvalidProfileError):
        f.build_features({"subjects": ["Java"]}, {"subjects": ["Java"], "expertise_level": 9})


def test_dataset_features_match_backend_definitions():
    """Training/inference consistency: every CSV row's pre-computed features equal
    what the backend's feature functions derive from the raw columns."""
    df = pd.read_csv(DATASET)
    for r in df.itertuples():
        assert f.subject_match([r.learner_subject], r.tutor_subjects.split("|")) == r.subject_match
        assert f.preference_match(r.learner_learning_preference, r.tutor_learning_preference) == r.preference_match
        assert f.availability_match([r.learner_availability], [r.tutor_availability]) == r.availability_match
