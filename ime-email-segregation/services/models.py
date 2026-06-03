from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EmailRecord(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    category = db.Column(db.String(50))

    raw_email = db.Column(db.Text)

    cargo_name = db.Column(db.String(200))
    
    vessel_name = db.Column(db.String(200))
    vessel_size = db.Column(db.String(100))
    open_port = db.Column(db.String(200))

    loading_port = db.Column(db.String(200))
    discharge_port = db.Column(db.String(200))
    laycan = db.Column(db.String(200))

    delivery_port = db.Column(db.String(200))
    redelivery_port = db.Column(db.String(200))
    duration = db.Column(db.String(200))