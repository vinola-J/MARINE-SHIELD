import pytest
from severity.severity import assess_pollution_severity


def test_severity_levels():
    for category in ["Plastic Waste", "Fishing Net", "Glass", "Metal", "Organic Waste", "Other Waste"]:
        res = assess_pollution_severity(
            prediction=category,
            confidence=0.85,
            visual_features={"clutter_score": 0.5, "edge_density": 0.5}
        )
        assert res["severity_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert 0.0 <= res["severity_score"] <= 1.0
        assert len(res["severity_reason"]) > 10
        assert "Prototype Severity Assessment" in res["assessment_type"]
        assert "disclaimer" in res


def test_fishing_net_high_hazard():
    res = assess_pollution_severity(
        prediction="Fishing Net",
        confidence=0.90,
        visual_features={"clutter_score": 0.8, "edge_density": 0.75}
    )
    # High clutter fishing net should result in HIGH severity
    assert res["severity_level"] == "HIGH"
    assert "entanglement" in res["severity_reason"].lower()


def test_low_confidence_dampening():
    res_normal = assess_pollution_severity(
        prediction="Fishing Net",
        confidence=0.95,
        visual_features={"clutter_score": 0.9, "edge_density": 0.9},
        is_low_confidence=False
    )
    res_dampened = assess_pollution_severity(
        prediction="Fishing Net",
        confidence=0.45,
        visual_features={"clutter_score": 0.9, "edge_density": 0.9},
        is_low_confidence=True
    )
    assert res_dampened["severity_score"] < res_normal["severity_score"]
    assert "manual physical inspection" in res_dampened["severity_reason"].lower()
