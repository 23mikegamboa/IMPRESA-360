# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from apps.home.models import Registro, Modelo
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import db
from datetime import datetime
from sqlalchemy import asc, func, case, cast, Integer, desc, or_

@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')

# VALIDATE VALUES
def get_value(field_name):
    value = request.form.get(field_name, "").strip()
    return value if value else "None"

# NEW: Customer view & add route
@blueprint.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():

    if request.method == "POST":
         # Convert to Python date objects (if provided)
        date_in_str = request.form.get("date_in")
        date_out_str = request.form.get("date_out")
        date_checklisted_str = request.form.get("date_checklisted")
        created_str = request.form.get("created")
        last_edited_str = request.form.get("last_edited")

        servici = get_value("servici")
        date_in = datetime.strptime(date_in_str, "%Y-%m-%d").date() if date_in_str else None
        date_out = datetime.strptime(date_out_str, "%Y-%m-%d").date() if date_out_str else None
        vin = get_value("vin")
        plate_no = get_value("plate_no")
        make = get_value("make")
        model = get_value("model")
        color = get_value("color")
        km_mileage = get_value("km_mileage")
        notes = get_value("notes")
        posizione = get_value("posizione")
        cliente = get_value("cliente")
        concerns_requests = get_value("concerns_requests")
        diagnosis = get_value("diagnosis")
        onsite_details = get_value("onsite_details")
        tagged = get_value("tagged")
        estimate = get_value("estimate")
        parts_and_materials = get_value("parts_and_materials")
        billing = get_value("billing")
        day_count = get_value("day_count")
        received_from = get_value("received_from")
        received_by = get_value("received_by")
        date_checklisted = datetime.strptime(date_checklisted_str, "%Y-%m-%d").date() if date_checklisted_str else None
        checklisted_by = get_value("checklisted_by")
        checklist = get_value("checklist")
        scartoffie = get_value("scartoffie")
        transazioni = get_value("transazioni")
        transazioni_intl = get_value("transazioni_intl")
        related_jo = get_value("related_jo")
        released_to = get_value("released_to")
        released_by = get_value("released_by")
        created = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S") if created_str else datetime.now()
        created_by = get_value("created_by")
        last_edited = datetime.strptime(last_edited_str, "%Y-%m-%d %H:%M:%S") if last_edited_str else datetime.now()
        last_edited_by = get_value("last_edited_by")
        
        if not (servici):
            flash("Servici required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (date_in):
            flash("Date In required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (make):
            flash("Make required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (color):
            flash("Color required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (posizione):
            flash("Posizione required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        # Check invalid date in & date out
        if date_in is not None and date_out is not None:
            if date_out < date_in:
                flash("Invalid date out.", "danger")
                # return redirect(url_for("home_blueprint.registro"))
        
        # Ensure Make/Model exist in Modelo table, else insert them
        existing_modelo = Modelo.query.filter_by(make=make, model=model).first()
        if not existing_modelo:
            new_modelo = Modelo(make=make, model=model)
            db.session.add(new_modelo)
            db.session.commit()

        # If unique, create new record
        new_registro = Registro(
            servici=servici, 
            date_in=date_in, 
            date_out=date_out, 
            vin=vin, 
            plate_no=plate_no, 
            make=make, 
            model=model, 
            color=color, 
            km_mileage=km_mileage, 
            notes=notes, 
            posizione=posizione,
            cliente=cliente, 
            concerns_requests=concerns_requests, 
            onsite_details=onsite_details,
            received_from=received_from, 
            received_by=received_by, 
            date_checklisted=date_checklisted, 
            checklisted_by=checklisted_by, 
            related_jo=related_jo, 
            released_to=released_to, 
            released_by=released_by,
            # auto-fill 
            tagged="No",
            diagnosis="PDD (Pending Diagnosis)", 
            estimate="Pending Estimate", 
            parts_and_materials="PPS (Parts Procurement Stage)", 
            billing="Pending Billing",  
            day_count=(datetime.today().date()-date_in).days, 
            checklist=checklist,
            scartoffie=scartoffie,
            transazioni=transazioni,
            transazioni_intl=transazioni_intl,
            #checklist="None", 
            #scartoffie="None", 
            #transazioni="None", 
            #transazioni_intl="None", 
            created=datetime.now(), 
            created_by=created_by, 
            last_edited=last_edited, 
            last_edited_by=last_edited_by
            )
        try:
            db.session.add(new_registro)
            db.session.commit()
            flash("Successfully added.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error: " + str(e), "danger")

        return redirect(url_for("home_blueprint.registro"))

    # Query all vehicle data
    modelo_data = Modelo.query.with_entities(Modelo.make, Modelo.model).distinct().all()

    # Convert to simple lists for dropdowns
    makes = sorted(set([m.make for m in modelo_data]))

    # Find last jo_no
    last_jo = db.session.query(func.max(cast(Registro.jo_no, Integer))).scalar() or 0
    next_jo = last_jo + 1

    # === NEW: SEARCH HANDLER ===
    search_field = request.args.get("field")
    search_query = request.args.get("query", "").strip()
    
    # Base query
    registro_query = Registro.query

    # If a search field & query are provided
    if search_field and search_query:
        field_map = {
            "jo_no": Registro.jo_no,
            "date_in": Registro.date_in,
            "date_out": Registro.date_out,
            "plate_no": Registro.plate_no,
            "vin": Registro.vin,
            "make": Registro.make,
            "model": Registro.model,
            "cliente": Registro.cliente,
            "posizione": Registro.posizione
        }

        if search_field in field_map:
            column = field_map[search_field]
            registro_query = registro_query.filter(func.lower(column).like(f"%{search_query}%"))

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 20

    registro_table = registro_query.order_by(
        # First: push numeric jo_no to the top (strings last)
        case(
            (Registro.jo_no.op('GLOB')('[0-9]*'), 0),  # numeric → 0
            else_=1                                    # strings → 1
        ),
        # Then: order numerics descending
        desc(cast(Registro.jo_no, Integer))
    ).paginate(page=page, per_page=per_page)
    
    return render_template('home/registro.html', 
                           segment='registro', 
                           #registro_data=registro_data,
                           registro_table=registro_table,
                           makes=makes,
                           next_jo=next_jo,
                           search_field=search_field,
                           search_query=search_query
                           )

@blueprint.route('/registro/edit/<int:jo_id>', methods=['GET', 'POST'])
@login_required
def edit_registro(jo_id):
    registro = Registro.query.get_or_404(jo_id)

    if request.method == "POST":

        # Convert dates safely
        date_in_str = request.form.get("date_in")
        date_out_str = request.form.get("date_out")
        date_checklisted_str = request.form.get("date_checklisted")
        created_str = request.form.get("created")
        last_edited_str = request.form.get("last_edited")

        registro.servici = get_value("servici")
        registro.jo_no = get_value("jo_no")
        registro.date_in = datetime.strptime(date_in_str, "%Y-%m-%d").date() if date_in_str else None
        registro.date_out = datetime.strptime(date_out_str, "%Y-%m-%d").date() if date_out_str else None
        registro.vin = get_value("vin")
        registro.make = get_value("make")
        registro.model = get_value("model")
        registro.plate_no = get_value("plate_no")
        registro.color = get_value("color")
        registro.notes = get_value("notes")
        registro.cliente = get_value("cliente")
        registro.tagged = get_value("tagged")
        registro.diagnosis = get_value("diagnosis")
        registro.estimate = get_value("estimate")
        registro.parts_and_materials = get_value("parts_and_materials")
        registro.billing = get_value("billing")
        registro.posizione = get_value("posizione")
        registro.day_count = get_value("day_count")
        registro.released_to = get_value("released_to")
        registro.received_from = get_value("received_from")
        registro.related_jo = get_value("related_jo")
        registro.received_by = get_value("received_by")
        registro.date_checklisted = datetime.strptime(date_checklisted_str, "%Y-%m-%d").date() if date_checklisted_str else None
        registro.checklisted_by = get_value("checklisted_by")
        registro.released_by = get_value("released_by")
        registro.km_mileage = get_value("km_mileage")
        registro.concerns_requests = get_value("concerns_requests")
        registro.scartoffie = get_value("scartoffie")
        registro.transazioni = get_value("transazioni")
        registro.transazioni_intl = get_value("transazioni_intl")
        registro.created = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S") if created_str else datetime.now()
        registro.last_edited = datetime.strptime(last_edited_str, "%Y-%m-%d %H:%M:%S") if last_edited_str else datetime.now()
        registro.created_by = get_value("created_by")
        registro.last_edited_by = get_value("last_edited_by")
        registro.checklist = get_value("checklist")
        registro.onsite_details = get_value("onsite_details")
        
        if not (registro.servici):
            flash("Servici required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (registro.jo_no):
            flash("J.O# required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (registro.date_in):
            flash("Date In required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (registro.make):
            flash("Make required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (registro.color):
            flash("Color required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))
        
        if not (registro.posizione):
            flash("Posizione required.", "danger")
            # return redirect(url_for("home_blueprint.registro"))

        # Check invalid date in & date out
        if registro.date_in is not None and registro.date_out is not None:
            if registro.date_out < registro.date_in:
                flash("Invalid date out.", "danger")
            #return redirect(url_for("home_blueprint.registro"))

        #Ensure Make/Model exist in Modelo table, else insert them
        make = registro.make
        model = registro.model
        if make and model:
            existing_modelo = Modelo.query.filter_by(make=make, model=model).first()
            if not existing_modelo:
                new_modelo = Modelo(make=make, model=model)
                db.session.add(new_modelo)
                db.session.commit()

        try:
            db.session.commit()
            flash("Updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating: " + str(e), "danger")

        return redirect(url_for("home_blueprint.registro"))

    #Pass makes for the dropdown in edit form too
    modelo_data = Modelo.query.with_entities(Modelo.make, Modelo.model).distinct().all()
    makes = sorted(set([m.make for m in modelo_data]))
    
    return render_template(
        "home/registro.html",
        segment="registro",
        registro=registro,
        makes=makes
    )

@blueprint.route('/registro/delete/<int:jo_id>', methods=['POST'])
@login_required
def delete_registro(jo_id):
    registro = Registro.query.get_or_404(jo_id)

    try:
        db.session.delete(registro)
        db.session.commit()
        flash("Deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting Job Order:" + str(e), "danger")

    return redirect(url_for("home_blueprint.registro"))

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
    
@blueprint.route('/get_models/<make>')
@login_required
def get_models(make):
    # Use explicit filter instead of filter_by, safer for case-sensitive fields
    models = (
        Modelo.query.with_entities(Modelo.model)
        .filter(Modelo.make == make)
        .distinct()
        .order_by(func.lower(Modelo.model)) 
        .all()
    )
    # Return list of model names (filter out None just in case)    
    return jsonify([m.model for m in models if m.model])