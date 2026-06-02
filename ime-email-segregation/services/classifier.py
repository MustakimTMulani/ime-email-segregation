def classify_email(text):

    text = text.upper()

    tonnage_score = 0
    cargo_vc_score = 0
    cargo_tc_score = 0

    # TONNAGE

    if any(x in text for x in ["MV ", "DWT"]):
     tonnage_score += 1

    if "OPEN" in text:
     tonnage_score += 1

    if "DWT" in text:
     tonnage_score += 1

# CARGO VC

    if any(x in text for x in ["LOAD PORT", "LP", "POL"]):
        cargo_vc_score += 1

    if any(x in text for x in ["DISCHARGE PORT", "DP", "POD"]):
        cargo_vc_score += 1

    if any(x in text for x in ["LAYCAN", "LC"]):
     cargo_vc_score += 1

    # CARGO TC

# CARGO TC

    if any(x in text for x in ["DELIVERY", "DELY"]):
     cargo_tc_score += 1

    if any(x in text for x in ["REDELIVERY", "REDEL"]):
     cargo_tc_score += 1

    if "DURATION" in text:
     cargo_tc_score += 1

    scores = {
        "Tonnage": tonnage_score,
        "Cargo VC": cargo_vc_score,
        "Cargo TC": cargo_tc_score
    }

    highest_score = max(scores.values())

    if highest_score == 0:

        return {
            "category": "Unknown",
            "scores": scores
        }

    category = max(
        scores,
        key=scores.get
    )

    return {
        "category": category,
        "scores": scores
    }