"""Model artifact loading and prediction."""
import joblib
import pytest
import sklearn

from app.ml import model_loader
from app.ml.features import FEATURE_ORDER
from app.ml.model_loader import ModelUnavailableError
from app.ml.predictor import predict_match_probabilities


@pytest.fixture(autouse=True)
def _fresh_cache():
    model_loader.reset_model_cache()
    yield
    model_loader.reset_model_cache()


def row(subject, expertise, pref, avail):
    return dict(zip(FEATURE_ORDER, [subject, expertise, pref, avail]))


def test_artifact_loads_with_expected_features():
    bundle = model_loader.get_model_bundle()
    assert bundle["features"] == FEATURE_ORDER
    assert bundle["sklearn_version"] == sklearn.__version__
    assert 1 in list(bundle["model"].classes_)


def test_model_is_cached_not_reloaded():
    assert model_loader.get_model_bundle() is model_loader.get_model_bundle()


def test_predictions_are_probabilities_in_input_order():
    rows = [row(1, 5, 1, 1), row(0, 1, 0, 0)]
    probs = predict_match_probabilities(rows)
    assert len(probs) == 2 and all(0.0 <= p <= 1.0 for p in probs)
    assert probs[0] > probs[1]


def test_empty_input_returns_empty_list():
    assert predict_match_probabilities([]) == []


def test_sanity_of_learned_behaviour_on_synthetic_labels():
    # Agreement with the SYNTHETIC labelling heuristic, not real-world validation.
    strong = predict_match_probabilities([row(1, 4, 1, 1)])[0]
    subject_only = predict_match_probabilities([row(1, 3, 0, 0)])[0]
    no_subject_typical = predict_match_probabilities([row(0, 3, 1, 1)])[0]
    assert strong > 0.9
    assert no_subject_typical < 0.5
    assert strong > subject_only


def test_model_alone_can_rate_subject_mismatch_high__why_hard_filter_exists():
    # In the synthetic data every row with subject_match=0, preference_match=1,
    # availability_match=1 and expertise=5 is labelled 'match' (a quirk of the labelling
    # heuristic), so the model rates it as a match. The backend therefore removes
    # tutors who do not teach a requested subject BEFORE the model is consulted.
    prob = predict_match_probabilities([row(0, 5, 1, 1)])[0]
    assert prob > 0.5


def test_missing_file_raises_clear_error(monkeypatch, tmp_path):
    monkeypatch.setattr(model_loader, "MODEL_PATH", tmp_path / "nope.joblib")
    with pytest.raises(ModelUnavailableError, match="not found"):
        model_loader.get_model_bundle()


def test_corrupt_file_raises_clear_error(monkeypatch, tmp_path):
    bad = tmp_path / "bad.joblib"
    bad.write_bytes(b"this is not a model")
    monkeypatch.setattr(model_loader, "MODEL_PATH", bad)
    with pytest.raises(ModelUnavailableError, match="Could not load"):
        model_loader.get_model_bundle()


def test_wrong_feature_order_is_rejected(monkeypatch, tmp_path):
    good = model_loader.load_model_bundle()
    swapped = tmp_path / "swapped.joblib"
    joblib.dump({"model": good["model"], "features": list(reversed(FEATURE_ORDER)),
                 "sklearn_version": sklearn.__version__}, swapped)
    monkeypatch.setattr(model_loader, "MODEL_PATH", swapped)
    with pytest.raises(ModelUnavailableError, match="feature order"):
        model_loader.get_model_bundle()


def test_sklearn_version_mismatch_is_rejected(monkeypatch, tmp_path):
    good = model_loader.load_model_bundle()
    old = tmp_path / "old.joblib"
    joblib.dump({"model": good["model"], "features": FEATURE_ORDER, "sklearn_version": "0.0.1"}, old)
    monkeypatch.setattr(model_loader, "MODEL_PATH", old)
    with pytest.raises(ModelUnavailableError, match="retrain"):
        model_loader.get_model_bundle()


def test_failed_load_is_cached(monkeypatch, tmp_path):
    monkeypatch.setattr(model_loader, "MODEL_PATH", tmp_path / "nope.joblib")
    with pytest.raises(ModelUnavailableError):
        model_loader.get_model_bundle()
    assert model_loader._error is not None
