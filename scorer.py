# scorer.py
# Combines results from all 3 layers to compute a final risk score (0–100) and status.

def compute_risk_score(kw_result: dict, pattern_result: dict, ai_result: dict) -> dict:
    """
    Layer weights:
      Layer 1 (keywords) : up to 35 points  (12 pts per keyword)
      Layer 2 (patterns) : up to 35 points  (18 pts per pattern)
      Layer 3 (AI check) : up to 30 points  (scaled by confidence)
    """
    score = 0
    breakdown = {}

    # Layer 1 — keywords
    kw_matches = kw_result.get("matches", [])
    kw_score = min(35, len(kw_matches) * 12)
    score += kw_score
    breakdown["layer1_keywords"] = {"score": kw_score, "matches": kw_matches}

    # Layer 2 — patterns
    pat_matches = pattern_result.get("matches", [])
    pat_score = min(35, len(pat_matches) * 18)
    score += pat_score
    breakdown["layer2_patterns"] = {"score": pat_score, "matches": pat_matches}

    # Layer 3 — AI semantic moderation
    ai_label      = ai_result.get("label", "SAFE").upper()
    ai_confidence = float(ai_result.get("confidence", 0.5))

    if ai_label == "MALICIOUS":
        ai_score = int(30 * ai_confidence)
    elif ai_label == "SUSPICIOUS":
        ai_score = int(15 * ai_confidence)
    else:
        ai_score = 0

    score += ai_score
    breakdown["layer3_ai"] = {
        "score":      ai_score,
        "label":      ai_label,
        "confidence": ai_confidence,
        "reason":     ai_result.get("reason", ""),
    }

    # Cap at 100
    score = min(100, score)

    if score >= 70:
        status = "MALICIOUS"
    elif score >= 30:
        status = "SUSPICIOUS"
    else:
        status = "SAFE"

    return {"score": score, "status": status, "breakdown": breakdown}
