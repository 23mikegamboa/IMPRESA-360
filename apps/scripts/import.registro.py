# apps/scripts/import_registro.py
import csv
import click
from datetime import datetime
from sqlalchemy import func, cast, Integer
from apps import db
from apps.home.models import Registro

# ---------- Helpers ----------

DATE_PATTERNS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%d-%b-%Y",  # 01-Oct-2025
    "%b %d, %Y", # Oct 01, 2025
]

BOOL_TRUE = {"true", "1", "yes", "y", "t", "✓", "checked"}
BOOL_FALSE = {"false", "0", "no", "n", "f", ""}

ALIASES = {
    # CSV Header  -> Registro model column
    "Servici": "servici",
    "J.O No.": "jo_no",
    "Date In": "date_in",
    "Date Out": "date_out",
    "VIN": "vin",
    "Plate No.": "plate_no",
    "Make": "make",
    "Model": "model",
    "Color": "color",
    "KM Mileage": "km_mileage",
    "Notes": "notes",
    "Posizione": "posizione",
    "Cliente": "cliente",
    "Concerns/Requests": "concerns_requests",
    "Diagnosis": "diagnosis",
    "On-site Details": "onsite_details",
    "Tagged": "tagged",
    "Estimate": "estimate",
    "Parts & Materials": "parts_and_materials",
    "Billing": "billing",
    "Days Count": "day_count",
    "Received From": "received_from",
    "Received By": "received_by",
    "Date Checklisted": "date_checklisted",
    "Checklisted By": "checklisted_by",
    "Checklist": "checklist",
    "Scartoffie": "scartoffie",
    "Transazioni": "transazioni",
    "Transazioni (Int'l)": "transazioni_intl",
    "Related J.O": "related_jo",
    "Released To": "released_to",
    "Released By": "released_by",
    "Created": "created",
    "Created by": "created_by",
    "Last edited": "last_edited",
    "Last edited by": "last_edited_by",
}

def _norm(s: str) -> str:
    return "".join(ch for ch in s.strip().lower() if ch.isalnum() or ch == " ").replace("  ", " ")

def _as_bool(val):
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in BOOL_TRUE:
        return True
    if s in BOOL_FALSE:
        return False
    return None

def _parse_date(val):
    if not val or str(val).strip() == "":
        return None
    txt = str(val).strip()
    # Try known formats first
    for p in DATE_PATTERNS:
        try:
            return datetime.strptime(txt, p).date()
        except ValueError:
            pass
    # Try best-effort parse (YYYYMMDD or DDMMYYYY numeric)
    only_digits = "".join(ch for ch in txt if ch.isdigit())
    if len(only_digits) == 8:
        # Try YYYYMMDD
        try:
            return datetime.strptime(only_digits, "%Y%m%d").date()
        except ValueError:
            pass
        # Try DDMMYYYY
        try:
            return datetime.strptime(only_digits, "%d%m%Y").date()
        except ValueError:
            pass
    # If still nothing, just return None (or raise if you prefer)
    return None

def _model_columns(model):
    return {c.name: c for c in model.__table__.columns}

def _resolve_header_to_column(h, model_cols):
    n = _norm(h)
    # Direct exact match
    if n in model_cols:
        return n
    # Alias match
    if n in ALIASES and ALIASES[n] in model_cols:
        return ALIASES[n]
    # Heuristic: remove spaces and dots to try again
    compact = n.replace(" ", "").replace(".", "").replace("#", "")
    for col in model_cols:
        if compact == col.replace("_", ""):
            return col
    return None

def _is_jo_no_integer():
    # Attempt to detect if jo_no column is Integer
    try:
        return isinstance(Registro.__table__.c.jo_no.type, Integer)
    except Exception:
        return False

def _next_jo_no():
    """
    Compute the next jo_no based on max(existing jo_no).
    Works whether jo_no is Integer or String containing integers.
    """
    try:
        # Try numeric cast first
        max_as_int = db.session.query(func.max(cast(Registro.jo_no, Integer))).scalar()
        if max_as_int is None:
            # Fallback: scan in Python
            max_num = 0
            for (val,) in db.session.query(Registro.jo_no).all():
                try:
                    n = int(str(val))
                    if n > max_num:
                        max_num = n
                except Exception:
                    continue
            return max_num + 1
        return max_as_int + 1
    except Exception:
        # Very defensive fallback
        return 1

# ---------- Importer ----------

def import_registro(csv_path, truncate=False, dry_run=False, on_duplicate="skip"):
    """
    on_duplicate: 'skip' | 'update' | 'fail'
    """
    model_cols = _model_columns(Registro)
    is_jo_int = _is_jo_no_integer()

    if truncate and not dry_run:
        click.echo("Truncating Registro…")
        db.session.query(Registro).delete()
        db.session.commit()

    created, updated, skipped = 0, 0, 0

    # Preload existing by jo_no to speed lookups
    existing_by_jo = {}
    if "jo_no" in model_cols:
        for r in db.session.query(Registro.jo_no, Registro.id if hasattr(Registro, "id") else Registro.jo_no).all():
            existing_by_jo[str(r[0])] = True

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Build header mapping
        header_map = {}
        for h in reader.fieldnames:
            col = _resolve_header_to_column(h, model_cols)
            header_map[h] = col

        click.echo("Header mapping:")
        for k, v in header_map.items():
            click.echo(f"  CSV '{k}'  ->  Model '{v}'")

        if dry_run:
            click.echo("\nDry run: No database changes will be made.\n")

        # Process rows
        for row in reader:
            data = {}

            # Map fields we recognize
            for src_h, dst_col in header_map.items():
                if not dst_col:
                    continue
                val = row.get(src_h)

                # Handle some known types
                if dst_col in {"date_in", "date_out", "date_checklisted", "created", "last_edited"}:
                    data[dst_col] = _parse_date(val)
                elif dst_col in {"paperwork", "checklisted"}:
                    data[dst_col] = _as_bool(val)
                elif dst_col in {"km_mileage"}:
                    try:
                        data[dst_col] = int(str(val).replace(",", "")) if val not in (None, "") else None
                    except Exception:
                        data[dst_col] = None
                else:
                    data[dst_col] = val if (val is not None and str(val).strip() != "") else None

            # jo_no handling (auto-generate if missing)
            if "jo_no" in model_cols:
                jo_val = data.get("jo_no")
                if jo_val is None or str(jo_val).strip() == "":
                    nxt = _next_jo_no()
                    data["jo_no"] = int(nxt) if is_jo_int else str(nxt)

            # Decide duplicate policy (based on jo_no if present)
            if "jo_no" in model_cols:
                key = str(data.get("jo_no"))
                exists = key in existing_by_jo
            else:
                exists = False
                key = None

            if exists:
                if on_duplicate == "skip":
                    skipped += 1
                    continue
                elif on_duplicate == "fail":
                    raise click.ClickException(f"Duplicate jo_no '{key}' encountered (on_duplicate=fail).")
                elif on_duplicate == "update":
                    if dry_run:
                        updated += 1
                        continue
                    # Update existing row by jo_no
                    obj = db.session.query(Registro).filter(Registro.jo_no == data["jo_no"]).first()
                    if obj:
                        for k, v in data.items():
                            if k == "jo_no":
                                continue
                            if k in model_cols:
                                setattr(obj, k, v)
                        updated += 1
                        continue

            # Create new
            if dry_run:
                created += 1
                continue

            obj = Registro()
            for k, v in data.items():
                if k in model_cols:
                    setattr(obj, k, v)
            db.session.add(obj)
            created += 1

        if dry_run:
            click.echo(f"\n[DRY RUN] Would create: {created}, update: {updated}, skip: {skipped}")
            db.session.rollback()
            return

        db.session.commit()
        click.echo(f"\nDone. Created: {created}, Updated: {updated}, Skipped: {skipped}")
