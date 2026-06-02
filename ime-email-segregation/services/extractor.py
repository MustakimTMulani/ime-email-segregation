import re

def split_opportunities(text):

    opportunities = re.split(

        r"\n\s*(?=(?:CARGO:|\d[\d,\-\s]*\s*MTS|1\s*TCT|A/C|ACC))",

        text,

        flags=re.IGNORECASE

    )

    return [
        block.strip()
        for block in opportunities
        if block.strip()
    ]

LOAD_PORT_LABELS = [
    "LOAD PORT",
    "LOADING PORT",
    "LP",
    "POL"
]

DISCHARGE_PORT_LABELS = [
    "DISCHARGE PORT",
    "DISCHARGING PORT",
    "DP",
    "POD"
]

LAYCAN_LABELS = [
    "LAYCAN",
    "LC"
]

def extract_account_name(text):

    patterns = [

    r"([A-Z][A-Z\s]+MARITIME\s+(?:INC|LTD|LLC|CO))",

    r"([A-Z][A-Z\s]+SHIPPING\s+(?:INC|LTD|LLC|CO))",

    r"([A-Z][A-Z\s]+CHARTERING\s+(?:INC|LTD|LLC|CO))",

    r"([A-Z][A-Z\s]+LOGISTICS\s+(?:INC|LTD|LLC|CO))",

    r"([A-Z][A-Z\s]+TRADING\s+(?:INC|LTD|LLC|CO))"

]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return (
                match.group(1)
                .strip()
            )

    return None


def extract_tonnage(text):

    records = []

    account_name = extract_account_name(text)

    # Pattern 1
    # MV SHENG AN HAI DWT 56564 OPEN XIAMEN, CHINA O/A 2ND JUNE 2026

    pattern1 = re.finditer(

        r"MV\s+([A-Z0-9\s]+?)\s+DWT\s+(\d+)\s+OPEN\s+([A-Z\s,]+?)\s+O/A\s+([A-Z0-9\s\-]+)",

        text,

        re.IGNORECASE

    )

    for match in pattern1:

        records.append({

            "account_name": account_name,

            "vessel_name": match.group(1).strip(),

            "vessel_size": match.group(2).strip(),

            "open_port": match.group(3).strip(),

            "open_date": match.group(4).strip(),

            "vessel_type": "Bulk Carrier"

        })

    # Pattern 2
    # MV TRUE FRIEND/51K/09 - BEJAIA , 1ST JUNE

    pattern2 = re.finditer(

        r"MV\s+([A-Z0-9\s]+?)\/(\d+)K.*?-\s*([A-Z\s]+?)\s*,\s*([0-9A-Z\s]+)",

        text,

        re.IGNORECASE

    )

    for match in pattern2:

        records.append({

            "account_name": account_name,

            "vessel_name": match.group(1).strip(),

            "vessel_size": match.group(2).strip() + "K",

            "open_port": match.group(3).strip(),

            "open_date": match.group(4).strip(),

            "vessel_type": "Bulk Carrier"

        })

    # Pattern 3
    # MV BLUE STAR (38K DWT) - OPEN 25 MAY GABES, TUNISIA

    pattern3 = re.finditer(

        r"MV\s+([A-Z0-9\s]+?)\s+\((\d+)K\s+DWT\)\s*-\s*OPEN\s+([0-9A-Z\s]+)\s+([A-Z\s,]+)",

        text,

        re.IGNORECASE

    )

    for match in pattern3:

        records.append({

            "account_name": account_name,

            "vessel_name": match.group(1).strip(),

            "vessel_size": match.group(2).strip() + "K",

            "open_date": match.group(3).strip(),

            "open_port": match.group(4).strip(),

            "vessel_type": "Bulk Carrier"

        })



    pattern4 = re.finditer(

    r"^([A-Z][A-Z ]+?)\s+\((\d+)K.*?\)\s*[–-]\s*OPEN\s+([A-Z\s,]+?)\s+(\d{1,2}-\d{1,2}\s+[A-Z]+)",

    text,

    re.IGNORECASE | re.MULTILINE

)

    for match in pattern4:

        records.append({

        "account_name": account_name,

        "vessel_name": match.group(1).strip(),

        "vessel_size": match.group(2).strip() + "K",

        "open_port": match.group(3).strip(),

        "open_date": match.group(4).strip(),

        "vessel_type": "Bulk Carrier"

    })

    return records


def extract_cargo_vc(text):

    account_name = extract_account_name(
    text
)

    records = []

    blocks = split_opportunities(
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

        if not cargo_match:

         cargo_match = re.search(
            r"\d[\d,\-\s]*\s*MTS\s+(.*?)(?:\n|$)",
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
            rf"(?:{'|'.join(LOAD_PORT_LABELS)})\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if load_match:

            loading_port = load_match.group(1).strip()

        discharge_match = re.search(
            rf"(?:{'|'.join(DISCHARGE_PORT_LABELS)})\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if discharge_match:

            discharge_port = (
                discharge_match.group(1).strip()
            )

        laycan_match = re.search(
            rf"(?:{'|'.join(LAYCAN_LABELS)})\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if laycan_match:

            laycan = laycan_match.group(1).strip()

        if (
            cargo_name
            or loading_port
            or discharge_port
                ):

            records.append({

                "account_name": account_name,

                "cargo_name": cargo_name,

                "cargo_type": "Bulk",

                "loading_port": loading_port,

                "discharge_port": discharge_port,

                "laycan": laycan

            })

    return records


def extract_cargo_tc(text):

    account_name = extract_account_name(
    text
)

    records = []

    blocks = split_opportunities(
    text
    )

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        delivery_port = None
        redelivery_port = None
        duration = None
        cargo_name = None
        laycan = None

        delivery_match = re.search(
            r"(?:DELIVERY|DELY)\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if delivery_match:

            delivery_port = (
                delivery_match.group(1)
                .strip()
            )

        redelivery_match = re.search(
            r"(?:REDELIVERY|REDEL)\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if redelivery_match:

            redelivery_port = (
                redelivery_match.group(1)
                .strip()
            )

        duration_match = re.search(
            r"(?:DURATION)\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if duration_match:

            duration = (
                duration_match.group(1)
                .strip()
            )

        cargo_match = re.search(
                 r"(?:CARGO|COMMODITY)\s*:?\s*(.+)",
                 block,
                re.IGNORECASE
)

        if not cargo_match:

            cargo_match = re.search(
              r"1\s*TCT\s*WITH\s*(.+)",
            block,
             re.IGNORECASE
    )

        if cargo_match:

            cargo_name = (
                cargo_match.group(1)
                .strip()
            )

        laycan_match = re.search(
            rf"(?:{'|'.join(LAYCAN_LABELS)})\s*:?\s*(.+)",
            block,
            re.IGNORECASE
        )

        if laycan_match:

            laycan = (
                laycan_match.group(1)
                .strip()
            )

        if (
            delivery_port
            or redelivery_port
            or duration
        ):

            records.append({

                "account_name": account_name,

                "delivery_port":
                delivery_port,

                "redelivery_port":
                redelivery_port,

                "duration":
                duration,

                "cargo_name":
                cargo_name,

                "laycan":
                laycan,

                "cargo_type":
                "Time Charter"

            })

    return records