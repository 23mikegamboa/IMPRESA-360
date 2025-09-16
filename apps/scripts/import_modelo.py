import csv
from apps import db
from apps.home.models import Modelo

# Path to your CSV file inside apps/scripts/
CSV_FILE = "apps/scripts/MODELO_UPDATED.csv"

def import_modelo():
    with open(CSV_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        count = 0
        for row in reader:
            modelo = Modelo(
                make=row.get("Make"),
                description=row.get("Description"),
                model=row.get("Model"),
                trim=row.get("Trim"),
                body=row.get("Body"),
                fuel_type=row.get("Fuel Type"),
                transmission=row.get("Transmission"),
                fuel_system=row.get("Fuel System"),
                drivetrain=row.get("Drivetrain"),
                engine_displacement=row.get("Engine Displacement"),
                cylinders=row.get("Cylinders"),
                description_2=row.get("Description*"),  # renamed in model
                submodel=row.get("Sub-model"),           # may be blank if column not in CSV
                generation=row.get("Generation"),
            )
            db.session.add(modelo)
            count += 1

        db.session.commit()
        print(f"✅ Imported {count} rows into Modelo table")

