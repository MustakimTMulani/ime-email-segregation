def classify_email(text):

    text = text.upper()

    tonnage_score = 0
    cargo_vc_score = 0
    cargo_tc_score = 0

    # TONNAGE

    if "MV " in text:
        tonnage_score += 1

    if "OPEN" in text:
        tonnage_score += 1

    if "DWT" in text:
        tonnage_score += 1

    # CARGO VC

    if "LOAD PORT" in text:
        cargo_vc_score += 1

    if "DISCHARGE PORT" in text:
        cargo_vc_score += 1

    if "LAYCAN" in text:
        cargo_vc_score += 1

    # CARGO TC

    if "DELIVERY" in text:
        cargo_tc_score += 1

    if "REDELIVERY" in text:
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