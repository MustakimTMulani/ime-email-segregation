from flask import Flask, render_template, request, jsonify
from services.classifier import classify_email
from services.extractor import (
    extract_tonnage,
    extract_cargo_vc,
    extract_cargo_tc
)
from services.models import db, EmailRecord
from services.pdf_reader import extract_pdf_text

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ime.db"

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/records")
def records():

    search = request.args.get("search")

    if search:

        data = EmailRecord.query.filter(

         (EmailRecord.vessel_name.contains(search)) |

         (EmailRecord.open_port.contains(search)) |

         (EmailRecord.loading_port.contains(search)) |

         (EmailRecord.discharge_port.contains(search)) |

         (EmailRecord.delivery_port.contains(search)) |

         (EmailRecord.redelivery_port.contains(search))

    ).all()

    else:

        data = EmailRecord.query.all()

    return render_template(
        "records.html",
        records=data
    )


@app.route("/dashboard")
def dashboard():

    total = EmailRecord.query.count()

    tonnage = EmailRecord.query.filter_by(
        category="Tonnage"
    ).count()

    cargo_vc = EmailRecord.query.filter_by(
        category="Cargo VC"
    ).count()

    cargo_tc = EmailRecord.query.filter_by(
        category="Cargo TC"
    ).count()

    vessels = EmailRecord.query.filter_by(
        category="Tonnage"
    ).count()

    cargos = EmailRecord.query.filter_by(
        category="Cargo VC"
    ).count()

    recommendation_count = (
        vessels * cargos
    )

    return render_template(

        "dashboard.html",

        total=total,

        tonnage=tonnage,

        cargo_vc=cargo_vc,

        cargo_tc=cargo_tc,

        recommendation_count=
        recommendation_count

    )

@app.route("/matches")
def matches():

    vessels = EmailRecord.query.filter_by(
        category="Tonnage"
    ).all()

    cargos = EmailRecord.query.filter_by(
        category="Cargo VC"
    ).all()

    matches = []

    for vessel in vessels:

        for cargo in cargos:

            criteria_met = 0

            total_criteria = 3

            port_match = False
            size_match = False
            availability_match = True

            # Port Match

            if (
                vessel.open_port and
                cargo.loading_port
            ):

                if (
                    vessel.open_port.upper()
                    ==
                    cargo.loading_port.upper()
                ):

                    port_match = True
                    criteria_met += 1

            # Size Match

            if vessel.vessel_size:

                try:

                    dwt = int(
                        vessel.vessel_size
                    )

                    if dwt >= 50000:

                        size_match = True
                        criteria_met += 1

                except:
                    pass

            # Availability

            criteria_met += 1

            score = int(
                (criteria_met / total_criteria)
                * 100
            )

            matches.append({

                "vessel":
                vessel.vessel_name,

                "cargo_port":
                cargo.loading_port,

                "port_match":
                port_match,

                "size_match":
                size_match,

                "availability_match":
                availability_match,

                "criteria_met":
                criteria_met,

                "total_criteria":
                total_criteria,

                "score":
                score

            })

    matches = sorted(
        matches,
        key=lambda x: x["score"],
        reverse=True
    )

    return render_template(
        "matches.html",
        matches=matches
    )


@app.route("/api-test")
def api_test():

    return render_template(
        "api_test.html"
    )



@app.route("/api/extract", methods=["POST"])
def api_extract():

    if not request.json:

        return jsonify({

            "success": False,

            "error":
            "JSON data is required"

        }), 400

    email_content = request.json.get(
        "email_content",
        ""
    )

    if not email_content.strip():

        return jsonify({

            "success": False,

            "error":
            "email_content is required"

        }), 400

    classification_result = classify_email(
        email_content
    )

    category = classification_result[
        "category"
    ]

    classification_scores = classification_result[
        "scores"
    ]

    extracted_data = []

    if category == "Tonnage":

        extracted_data = extract_tonnage(
            email_content
        )

    elif category == "Cargo VC":

        extracted_data = extract_cargo_vc(
            email_content
        )

    elif category == "Cargo TC":

        extracted_data = extract_cargo_tc(
            email_content
        )

    if (
        isinstance(extracted_data, list)
        and
        len(extracted_data) > 0
    ):

        fields_found = len(

            [

                value

                for value in
                extracted_data[0].values()

                if value

            ]

        )

        total_expected_fields = len(
            extracted_data[0]
        )

    else:

        fields_found = 0

        total_expected_fields = 0

    confidence = 0

    if total_expected_fields > 0:

        confidence = int(

            (
                fields_found
                /
                total_expected_fields
            )
            * 100

        )

    return jsonify({

        "success": True,

        "category": category,

        "classification_scores":
        classification_scores,

        "confidence":
        confidence,

        "fields_found":
        fields_found,

        "total_expected_fields":
        total_expected_fields,

        "records":
        extracted_data

    })


@app.route("/upload", methods=["POST"])
def upload():

    uploaded_file = request.files["email_file"]

    filename = uploaded_file.filename.lower()

    if filename.endswith(".pdf"):

        text = extract_pdf_text(uploaded_file)

    else:

        text = uploaded_file.read().decode("utf-8")

    existing = EmailRecord.query.filter_by(
        raw_email=text
    ).first()

    if existing:

        return render_template(
            "result.html",
            category="Duplicate Email",
            extracted_data={
                "message": "This email already exists."
            }
        )

    category = classify_email(text)

    extracted_data = {}

    if category == "Tonnage":

        extracted_data = extract_tonnage(text)

        record = EmailRecord(
            category=category,
            raw_email=text,
            vessel_name=extracted_data.get("vessel_name"),
            vessel_size=extracted_data.get("vessel_size"),
            open_port=extracted_data.get("open_port")
        )

        db.session.add(record)
        db.session.commit()

    elif category == "Cargo VC":

        extracted_data = extract_cargo_vc(text)

        record = EmailRecord(
            category=category,
            raw_email=text,
            loading_port=extracted_data.get("loading_port"),
            discharge_port=extracted_data.get("discharge_port"),
            laycan=extracted_data.get("laycan")
        )

        db.session.add(record)
        db.session.commit()

    elif category == "Cargo TC":

        extracted_data = extract_cargo_tc(text)

        record = EmailRecord(
            category=category,
            raw_email=text,
            delivery_port=extracted_data.get("delivery_port"),
            redelivery_port=extracted_data.get("redelivery_port"),
            duration=extracted_data.get("duration")
        )

        db.session.add(record)
        db.session.commit()

    return render_template(
        "result.html",
        category=category,
        extracted_data=extracted_data
    )

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)