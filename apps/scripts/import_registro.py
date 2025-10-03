import csv
from apps import db
from apps.home.models import Registro
from datetime import datetime

# Path to your CSV file inside apps/scripts/
CSV_FILE = "apps/scripts/REGISTRO.csv"

def parse_date(value):
    if not value or value.strip() == "":
        return None
    try:
        # Adjust the format string to match your CSV (looks like DD/MM/YYYY)
        return datetime.strptime(value.strip(), "%m/%d/%Y").date()
    except ValueError:
        # fallback: try MM/DD/YYYY if needed
        try:
            return datetime.strptime(value.strip(), "%m/%d/%Y").date()
        except ValueError:
            return None  # or raise

def import_registro():
    Registro.query.delete()
    with open(CSV_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        count = 0
        for row in reader:
            registro = Registro(
                jo_id=row.get("JO_ID"),
                servici=row.get("Servici"), 
                jo_no=row.get("J.O No."),
                date_in=parse_date(row.get("Date In")),
                date_out=parse_date(row.get("Date Out")),
                vin=row.get("VIN"),
                plate_no=row.get("Plate No."),
                make=row.get("Make"),
                model=row.get("Model"),
                color=row.get("Color"),
                km_mileage=row.get("KM Mileage"),
                notes=row.get("Notes"),
                posizione=row.get("Posizione"),
                cliente=row.get("Cliente"),
                concerns_requests=row.get("Concerns/Requests"),
                diagnosis=row.get("Diagnosis"),
                onsite_details=row.get("On-site Details"),
                tagged=row.get("Tagged"),
                estimate=row.get("Estimate"),
                parts_and_materials=row.get("Parts & Materials"),
                billing=row.get("Billing"),
                day_count=row.get("Days Count"),
                received_from=row.get("Received From"),
                received_by=row.get("eceived By"),
                date_checklisted=parse_date(row.get("Date Checklisted")),
                checklisted_by=row.get("Checklisted By"),
                checklist=row.get("Checklist"),
                scartoffie=row.get("Scartoffie"),
                transazioni=row.get("Transazioni"),
                transazioni_intl=row.get("Transazioni (Int'l)"),
                related_jo=row.get("Related J.O"),
                released_to=row.get("Released To"),
                released_by=row.get("Released By"),
                created=parse_date(row.get("Created")),
                created_by=row.get("Created by"),
                last_edited=parse_date(row.get("Last edited")),
                last_edited_by=row.get("Last edited by"),
            )
            db.session.add(registro)
            count += 1

        db.session.commit()
        print(f"✅ Imported {count} rows into Registro table")