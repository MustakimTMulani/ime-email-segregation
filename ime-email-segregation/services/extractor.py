import re


def extract_tonnage(text):

    records = []

    account_name = None

    account_match = re.search(
        r"([A-Z\s]+MARITIME[A-Z\s]+)",
        text,
        re.IGNORECASE
    )

    if account_match:

        account_name = (
            account_match.group(1)
            .strip()
        )

    pattern = re.finditer(

        r"MV\s+([A-Z0-9\s]+?)\s+DWT\s+(\d+)\s+OPEN\s+([A-Z\s,]+?)\s+O/A\s+(.+)",

        text,

        re.IGNORECASE
    )

    for match in pattern:

        records.append({

            "account_name":
            account_name,

            "vessel_name":
            match.group(1).strip(),

            "vessel_size":
            match.group(2).strip(),

            "open_port":
            match.group(3).strip(),

            "open_date":
            match.group(4).strip(),

            "vessel_type":
            "Bulk Carrier"

        })

    return records


def extract_cargo_vc(text):

    records = []

    blocks = re.split(
        r"\n\s*\n",
        text
    )

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        cargo_name = None
        loading_port = None
        discharge_port = None
        laycan = None

        cargo_match = re.search(
            r"(?:mts|MTS)\s+(.*?)\s+(?:in bulk|bulk)",
            block,
            re.IGNORECASE
        )

        if cargo_match:

            cargo_name = (
                cargo_match.group(1)
                .replace("of ", "")
                .strip()
            )

        load_match = re.search(
            r"(?:LOAD PORT|LP|POL)\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if load_match:

            loading_port = load_match.group(1).strip()

        discharge_match = re.search(
            r"(?:DISCHARGE PORT|DP|POD)\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if discharge_match:

            discharge_port = (
                discharge_match.group(1).strip()
            )

        laycan_match = re.search(
            r"(?:LAYCAN|LC)\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if laycan_match:

            laycan = laycan_match.group(1).strip()

        if cargo_name:

            records.append({

                "account_name": None,

                "cargo_name": cargo_name,

                "cargo_type": "Bulk",

                "loading_port": loading_port,

                "discharge_port": discharge_port,

                "laycan": laycan

            })

    return records


def extract_cargo_tc(text):

    result = {}

    delivery_match = re.search(
        r"DELIVERY\s+(.+)",
        text,
        re.IGNORECASE
    )

    if delivery_match:
        result["delivery_port"] = delivery_match.group(1).strip()

    redelivery_match = re.search(
        r"REDELIVERY\s+(.+)",
        text,
        re.IGNORECASE
    )

    if redelivery_match:
        result["redelivery_port"] = redelivery_match.group(1).strip()

    duration_match = re.search(
        r"DURATION\s+(.+)",
        text,
        re.IGNORECASE
    )

    if duration_match:
        result["duration"] = duration_match.group(1).strip()

    return result