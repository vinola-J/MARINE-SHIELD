from typing import Dict, Any, Optional


# Inherent environmental hazard weight by waste type (0.0 - 1.0)
# e.g., Ghost fishing nets cause immediate lethal entanglement to marine fauna;
# plastics fragment into persistent microplastics; metals leach oxidization products.
CATEGORY_HAZARD_WEIGHTS = {
    "Fishing Net": 0.85,
    "Plastic Waste": 0.70,
    "Metal": 0.65,
    "Glass": 0.50,
    "Organic Waste": 0.35,
    "Other Waste": 0.55
}


def assess_pollution_severity(
    prediction: str,
    confidence: float,
    visual_features: Optional[Dict[str, Any]] = None,
    is_low_confidence: bool = False
) -> Dict[str, Any]:
    """
    Explainable rule-based Prototype Severity Assessment.
    
    Combines:
    1. Inherent ecological threat of the pollution category
    2. Image visual clutter, edge density, and contrast proxy
    3. Prediction confidence weighting
    
    Returns structured severity level (LOW, MEDIUM, HIGH), numeric score, and explainable rationale.
    """
    visual_features = visual_features or {}
    clutter = float(visual_features.get("clutter_score", 0.5))
    edge_density = float(visual_features.get("edge_density", 0.5))
    
    # 1. Base category ecological risk
    base_hazard = CATEGORY_HAZARD_WEIGHTS.get(prediction, 0.55)

    # 2. Coverage & fragmentation proxy from visual features
    # Higher edge density and clutter indicate widespread debris or multiple broken fragments
    density_factor = 0.6 * clutter + 0.4 * edge_density

    # 3. Composite score calculation (0.0 to 1.0)
    # Blend base hazard (55%) with visual distribution proxy (45%)
    composite_score = (0.55 * base_hazard) + (0.45 * density_factor)

    # If confidence is very low, dampen the extreme scores toward moderate triage
    if is_low_confidence:
        composite_score = (composite_score * 0.7) + (0.5 * 0.3)

    composite_score = round(min(1.0, max(0.05, composite_score)), 3)

    # 4. Determine qualitative level
    if composite_score < 0.40:
        severity_level = "LOW"
        level_desc = "Limited visible pollution footprint"
    elif composite_score < 0.70:
        severity_level = "MEDIUM"
        level_desc = "Moderate accumulation or localized multi-item debris"
    else:
        severity_level = "HIGH"
        level_desc = "Dense concentration, high-risk debris type, or widespread dispersal"

    # 5. Formulate transparent reasoning
    reasons = [f"{level_desc} for detected '{prediction}'."]
    if prediction == "Fishing Net":
        reasons.append("Monofilament netting poses immediate high-risk entanglement hazards to marine mammals, turtles, and sea birds (ghost fishing).")
    elif prediction == "Plastic Waste":
        if density_factor > 0.6:
            reasons.append("Multi-item or fragmented plastic distribution indicates elevated photodegradation and microplastic dispersion potential.")
        else:
            reasons.append("Synthetic polymer item poses long-term marine persistence and ingestion risks for coastal organisms.")
    elif prediction == "Metal":
        reasons.append("Oxidizing metal material creates sharp physical hazards for coastal fauna and human visitors, plus potential localized mineral leaching.")
    elif prediction == "Glass":
        reasons.append("Physical laceration hazard along intertidal zone; low chemical leach risk but durable physical hazard.")
    elif prediction == "Organic Waste":
        if density_factor > 0.7:
            reasons.append("Dense biomass accumulation can deplete dissolved oxygen (anoxia) during decomposition in enclosed coastal waters.")
        else:
            reasons.append("Organic matter is biodegradable; low acute ecological risk unless concentrated in stagnant zones.")
    else:
        reasons.append("Unclassified or composite waste item requiring manual shoreline verification and cataloging.")

    if is_low_confidence:
        reasons.append("Notice: Confidence is below standard threshold; manual physical inspection is recommended before dispatching specialized cleanup equipment.")

    severity_reason = " ".join(reasons)

    return {
        "severity_level": severity_level,
        "severity_score": composite_score,
        "severity_reason": severity_reason,
        "assessment_type": "Prototype Severity Assessment",
        "disclaimer": "Prototype Severity Assessment — rule-based estimation for triage; not a scientifically validated regulatory severity index.",
        "metrics_used": {
            "category_hazard_weight": base_hazard,
            "visual_density_proxy": round(density_factor, 3),
            "confidence_dampened": is_low_confidence
        }
    }
