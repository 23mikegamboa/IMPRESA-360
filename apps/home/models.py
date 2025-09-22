from apps import db
from datetime import date

class Registro(db.Model):
    __tablename__ = 'registro'

    #int_col_primary_key = db.Column(db.Integer, primary_key=True)
    #string_col_not_nullable = db.Column(db.String(120), nullable=False)
    #string_col_nullable = db.Column(db.String(120), nullable=True)
    #string_col_unique = db.Column(db.String(120), unique=True, nullable=False)
    #string_col_not_unique = db.Column(db.String(120), unique=False, nullable=False)
    #date_col = db.Column(db.Date)
    #bool_col = db.Column(db.Boolean, default=False) 
    #timestamp_col = 
    
    servici = db.Column(db.String(20))
    jo_no = db.Column(db.Integer, primary_key=True)
    date_in = db.Column(db.Date, nullable=False)
    date_out = db.Column(db.Date)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    plate_no = db.Column(db.String(100))
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    color = db.Column(db.String(100))
    km_mileage = db.Column(db.Integer)
    notes = db.Column(db.String(200))
    posizione = db.Column(db.String(100))
    cliente = db.Column(db.String(100))
    concerns_requests = db.Column(db.String(200))
    diagnosis = db.Column(db.String(100))
    onsite_details = db.Column(db.String(100))
    tagged = db.Column(db.String(10))
    paperwork = db.Column(db.String(10))
    estimate = db.Column(db.String(100))
    parts_and_materials = db.Column(db.String(100))
    billing = db.Column(db.String(100))
    day_count = db.Column(db.Integer)
    received_from = db.Column(db.String(100))
    received_by = db.Column(db.String(100))
    date_checklisted = db.Column(db.Date)
    checklisted_by = db.Column(db.String(100))
    checklist = db.Column(db.String(100))
    scartoffie = db.Column(db.String(100))
    transazioni = db.Column(db.String(100))
    transazioni_intl = db.Column(db.String(100))
    related_jo = db.Column(db.Integer)
    released_to = db.Column(db.String(100))
    released_by = db.Column(db.String(100))
    created = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    last_edited = db.Column(db.String(100))
    last_edited_by = db.Column(db.String(100))

    def __repr__(self):
        return f'<Registro {self.name}>'
    
class Modelo(db.Model):
    modelo_id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100))
    description = db.Column(db.String(200))
    model = db.Column(db.String(100))
    trim = db.Column(db.String(100))
    body = db.Column(db.String(50))
    fuel_type = db.Column(db.String(50))
    transmission = db.Column(db.String(200))
    fuel_system = db.Column(db.String(50))
    drivetrain = db.Column(db.String(50))
    engine_displacement = db.Column(db.String(50))
    cylinders = db.Column(db.String(50))
    description_2 = db.Column(db.String(200))
    submodel = db.Column(db.String(100))
    generation = db.Column(db.String(100))

    def __repr__(self):
        return f'<Modelo {self.name}>'
