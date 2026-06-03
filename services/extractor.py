import re

def split_opportunities(text):

    opportunities = re.split(

        r"\n\s*(?=(?:CARGO:|COMMODITY:|STEM:|\d[\d,\-\s]*\s*MTS|1\s*TCT|A/C|ACC))",

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

    r"MV\s+([A-Z0-9\s]+?)\s+DWT\s+(\d+)\s+OPEN\s+([A-Z\s,]+?)\s+O/A\s+([^\n\r]+)",

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
        
    pattern5 = re.finditer(

    r"MV\s+([A-Z\s]+?)\s+(\d{4,6})\s*DWT\s+OPEN\s+([A-Z\s]+?)\s+((?:PROMPT)|(?:\d{1,2}(?:-\d{1,2})?\s+[A-Z]+))",

    text,

    re.IGNORECASE | re.DOTALL

)

    for match in pattern5:

        records.append({

        "account_name": account_name,

        "vessel_name": match.group(1).strip(),

        "vessel_size": match.group(2).strip(),

        "open_port": match.group(3).strip(),

        "laycan": match.group(4).strip(),

        "vessel_type": "Bulk Carrier"

    })

    pattern6 = re.finditer(

    r"MV\s+([A-Z\s]+?)\s+"
    r"(?:ABOUT|ABT)?\s*"
    r"(\d{2,3},?\d{3})\s*DWT.*?"
    r"OPEN(?:\s+PORT)?\s*:?\s*"
    r"([A-Z\s]+?)\s+"
    r"(?:AVAILABLE|ETA|READY)?\s*:?\s*"
    r"((?:PROMPT)|(?:\d{1,2}(?:-\d{1,2})?\s+[A-Z]+))",

    text,

    re.IGNORECASE | re.DOTALL

)

    for match in pattern6:

        records.append({

        "account_name": account_name,

        "vessel_name": match.group(1).strip(),

        "vessel_size": match.group(2).replace(",", "").strip(),

        "open_port": match.group(3).strip(),

        "laycan": match.group(4).strip(),

        "vessel_type": "Bulk Carrier"

    })

    pattern7 = re.finditer(

    r"M\/?V\s+([A-Z\s]+?)\s+"
    r"(?:ABT|ABOUT)?\s*(\d+)K\s*DWT.*?"
    r"(?:OPEN|OPN)\s*:?\s*([A-Z\s]+?)\s+"
    r"(PROMPT|\d{1,2}(?:-\d{1,2})?\s+[A-Z]+)",

    text,

    re.IGNORECASE | re.DOTALL

)

    for match in pattern7:

        records.append({

        "account_name": account_name,

        "vessel_name": match.group(1).strip(),

        "vessel_size": match.group(2).strip() + "K",

        "open_port": match.group(3).strip(),

        "laycan": match.group(4).strip(),

        "vessel_type": "Bulk Carrier"

    })
    pattern8 = re.finditer(

    r"MV\s+([A-Z\s]+?).*?"
    r"(\d{2,3},?\d{3})\s*DWT.*?"
    r"OPEN\s+([A-Z\s]+).*?"
    r"(?:READY|ETA)\s*:?\s*([^\n\r]+)",

    text,

    re.IGNORECASE | re.DOTALL

)

    for match in pattern8:

     records.append({

        "account_name": account_name,

        "vessel_name": match.group(1).strip(),

        "vessel_size": match.group(2).replace(",", "").strip(),

        "open_port": match.group(3).strip(),

        "laycan": match.group(4).strip(),

        "vessel_type": "Bulk Carrier"

    })
    pattern9 = re.finditer(

    r"MV\s+([A-Z\s]+?)\s+"
    r"(\d{4,6})\s*DWT.*?"
    r"OPEN\s*:?\s*"
    r"([A-Z\s]+?)\s+"
    r"(PROMPT|\d{1,2}(?:-\d{1,2})?\s+[A-Z]+)",

    text,

    re.IGNORECASE | re.DOTALL

)

    for match in pattern9:

     records.append({

        "account_name": account_name,

        "vessel_name": match.group(1).strip(),

        "vessel_size": match.group(2).strip(),

        "open_port": match.group(3).strip(),

        "laycan": match.group(4).strip(),

        "vessel_type": "Bulk Carrier"

    })
    pattern10 = re.finditer(

    r"MV\s+([A-Z\s]+?)\s+"
    r"(\d+)K\s*DWT.*?"
    r"OPEN\s+PORT\s*:?\s*"
    r"([A-Z\s]+?)\s+"
    r"(?:AVAILABLE|READY|ETA)\s*:?\s*"
    r"([^\n\r]+)",

    text,

    re.IGNORECASE | re.DOTALL

)

    for match in pattern10:

     records.append({

        "account_name": account_name,

        "vessel_name": match.group(1).strip(),

        "vessel_size": match.group(2).strip() + "K",

        "open_port": match.group(3).strip(),

        "laycan": match.group(4).strip(),

        "vessel_type": "Bulk Carrier"

    })

    # Remove duplicates

    unique_records = []
    seen = set()

    for record in records:

        vessel_name = record.get(
            "vessel_name",
            ""
        ).strip().upper()

        vessel_size = record.get(
            "vessel_size",
            ""
        ).strip().upper()

        open_port = record.get(
            "open_port",
            ""
        ).strip().upper()

        key = (
            vessel_name,
            vessel_size,
            open_port
        )

        if (
            vessel_name
            and
            len(vessel_name) > 2
            and
            key not in seen
        ):

            seen.add(key)

            unique_records.append(
                record
            )

    return unique_records


def extract_cargo_vc(text):

    account_name = extract_account_name(text)

    records = []

    blocks = split_opportunities(text)

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        cargo_name = None
        loading_port = None
        discharge_port = None
        laycan = None

        # Pattern 1
        # 35000 MTS PETCOKE IN BULK

        cargo_match = re.search(

            r"(?:mts|MTS)\s+(.*?)\s+(?:in bulk|bulk)",

            block,

            re.IGNORECASE

        )

        # Pattern 2
        # 35000 MTS PETCOKE

        if not cargo_match:

            cargo_match = re.search(

                r"\d[\d,\-\s]*\s*MTS\s+(.*?)(?:\n|$)",

                block,

                re.IGNORECASE

            )

        # Pattern 3
        # COMMODITY: GYPSUM

        if not cargo_match:

            cargo_match = re.search(

                r"COMMODITY\s*:?\s*\n\s*([A-Z][A-Z\s]+)",

                block,

                re.IGNORECASE

            )

        # Pattern 4
        # CARGO: PETCOKE

        if not cargo_match:

            cargo_match = re.search(

                r"CARGO\s*:?\s*\n\s*([A-Z][A-Z\s]+)",

                block,

                re.IGNORECASE

            )

        # Pattern 5
        # ABT 35000 MTS OF COAL

        if not cargo_match:

            cargo_match = re.search(

                r"MTS\s+OF\s+([A-Z\s]+)",

                block,

                re.IGNORECASE

            )

# Pattern 6
# Disabled because it causes false positives

        if not cargo_match:

            cargo_match = None

        # Pattern 7
        # STEM: GYPSUM

        if not cargo_match:

            cargo_match = re.search(

                r"STEM\s*:?\s*(.+)",

                block,

                re.IGNORECASE

            )

        # Pattern 8
        # Standalone Cargo Name

        if not cargo_match:

            lines = block.splitlines()

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                if "@" in line:
                    continue

                if ":" in line:
                    continue

                if line.endswith(":"):
                    continue

                upper_line = line.upper()

                if any(label in upper_line for label in [

                    "LOAD",
                    "LOADPORT",
                    "LOADING",
                    "DISCH",
                    "DISPORT",
                    "DISCHARGE",
                    "POL",
                    "POD",
                    "LAYCAN",
                    "LAYDAYS",
                    "LC",
                    "QTY",
                    "MTS",
                    "STEM",
                    "COMMODITY",
                    "CARGO"

                ]):
                    continue

                cargo_name = line

                break

        if cargo_match:

            cargo_name = cargo_match.group(1)

            cargo_name = cargo_name.replace(
                "OF ",
                ""
            )

            cargo_name = cargo_name.strip()

        # LOAD PORTS

        load_match = re.search(

            r"(?:LOAD PORT|LOADING PORT|LOADPORT|LOAD|LP|POL)\s*:?\s*(.+)",

            block,

            re.IGNORECASE

        )

        if load_match:

            loading_port = load_match.group(1).strip()

        # DISCHARGE PORTS

        discharge_match = re.search(

            r"(?:DISPORT|DISCHARGE PORT|DISCHARGING PORT|DISCH|DP|POD)\s*:?\s*(.+)",

            block,

            re.IGNORECASE

        )

        if discharge_match:

            discharge_port = discharge_match.group(1).strip()

        # LAYCAN

        laycan_match = re.search(

            r"(?:LAYCAN|LAYDAYS|LC)\s*:?\s*(.+)",

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

    account_name = extract_account_name(text)

    records = []

    blocks = split_opportunities(text)

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        delivery_port = None
        redelivery_port = None
        duration = None
        cargo_name = None
        laycan = None

        # ---------------------------------
        # DELIVERY PATTERNS
        # ---------------------------------

        delivery_match = re.search(

            r"(?:DELIVERY|DELY|DEL)\s*:?\s*(.+)",

            block,

            re.IGNORECASE

        )

        if delivery_match:

            delivery_port = (
                delivery_match.group(1)
                .strip()
            )

        # ---------------------------------
        # REDELIVERY PATTERNS
        # ---------------------------------

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

        # ---------------------------------
        # DURATION / PERIOD PATTERNS
        # ---------------------------------

        duration_match = re.search(

            r"(?:DURATION|PERIOD|TRIP DURATION)\s*:?\s*(.+)",

            block,

            re.IGNORECASE

        )

        if duration_match:

            duration = (
                duration_match.group(1)
                .strip()
            )

        # ---------------------------------
        # CARGO PATTERN 1
        # CARGO: COAL
        # ---------------------------------

        cargo_match = re.search(

            r"(?:CARGO|COMMODITY)\s*:?\s*(.+)",

            block,

            re.IGNORECASE

        )

        # ---------------------------------
        # CARGO PATTERN 2
        # 1 TCT WITH COAL
        # ---------------------------------

        if not cargo_match:

            cargo_match = re.search(

                r"1\s*TCT\s*WITH\s*(.+)",

                block,

                re.IGNORECASE

            )

        # ---------------------------------
        # CARGO PATTERN 3
        # PETCOKE
        # DEL: FUJAIRAH
        # ---------------------------------

        if not cargo_match:

            cargo_match = re.search(

                r"^([A-Z][A-Z\s]{3,})$",

                block,

                re.MULTILINE

            )

        # ---------------------------------
        # CARGO PATTERN 4
        # TC REQUIREMENT FOR COAL
        # ---------------------------------

        if not cargo_match:

            cargo_match = re.search(

                r"TC\s+REQUIREMENT\s+FOR\s+(.+)",

                block,

                re.IGNORECASE

            )

        # ---------------------------------
        # CARGO PATTERN 5
        # BUSINESS: GYPSUM
        # ---------------------------------

        if not cargo_match:

            cargo_match = re.search(

                r"BUSINESS\s*:?\s*(.+)",

                block,

                re.IGNORECASE

            )

        # ---------------------------------
        # CARGO PATTERN 6
        # REQUIREMENT: IRON ORE
        # ---------------------------------

        if not cargo_match:

            cargo_match = re.search(

                r"REQUIREMENT\s*:?\s*(.+)",

                block,

                re.IGNORECASE

            )

        # ---------------------------------
        # CARGO PATTERN 7
        # COAL / PETCOKE
        # ---------------------------------

        if not cargo_match:

            cargo_match = re.search(

                r"([A-Z\s]+(?:COAL|PETCOKE|GYPSUM|IRON ORE|FERTILIZER)[A-Z\s]*)",

                block,

                re.IGNORECASE

            )

        if cargo_match:

            cargo_name = (
                cargo_match.group(1)
                .strip()
            )

        # ---------------------------------
        # LAYCAN PATTERNS
        # ---------------------------------

        laycan_match = re.search(

            r"(?:LAYCAN|LAYDAYS|LC)\s*:?\s*(.+)",

            block,

            re.IGNORECASE

        )

        if laycan_match:

            laycan = (
                laycan_match.group(1)
                .strip()
            )

        # ---------------------------------
        # SAVE RECORD
        # ---------------------------------

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