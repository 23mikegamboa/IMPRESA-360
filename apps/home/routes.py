# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from apps.home.models import Registro
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import db
from apps.home.models import Modelo
from datetime import datetime
from sqlalchemy import asc, func

@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')

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

        servici = request.form.get("servici")
        jo_no = request.form.get("jo_no")
        date_in = datetime.strptime(date_in_str, "%Y-%m-%d").date() if date_in_str else None
        date_out = datetime.strptime(date_out_str, "%Y-%m-%d").date() if date_out_str else None
        vin = request.form.get("vin")
        plate_no = request.form.get("plate_no")
        make = request.form.get("make")
        model = request.form.get("model")
        color = request.form.get("color")
        km_mileage = request.form.get("km_mileage")
        notes = request.form.get("notes")
        posizione = request.form.get("posizione")
        cliente = request.form.get("cliente")
        concerns_requests = request.form.get("concerns_requests")
        diagnosis = request.form.get("diagnosis")
        onsite_details = request.form.get("onsite_details")
        tagged = request.form.get("tagged")
        paperwork = request.form.get("paperwork")
        estimate = request.form.get("estimate")
        parts_and_materials = request.form.get("parts_and_materials")
        billing = request.form.get("billing")
        day_count = request.form.get("day_count")
        received_from = request.form.get("received_from")
        received_by = request.form.get("received_by")
        date_checklisted = datetime.strptime(date_checklisted_str, "%Y-%m-%d").date() if date_checklisted_str else None
        checklisted_by = request.form.get("checklisted_by")
        checklist = request.form.get("checklist")
        scartoffie = request.form.get("scartoffie")
        transazioni = request.form.get("transazioni")
        transazioni_intl = request.form.get("transazioni_intl")
        related_jo = request.form.get("related_jo")
        released_to = request.form.get("released_to")
        released_by = request.form.get("released_by")
        created = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S") if created_str else datetime.now()
        created_by = request.form.get("created_by")
        last_edited = datetime.strptime(last_edited_str, "%Y-%m-%d %H:%M:%S") if last_edited_str else datetime.now()
        last_edited_by = request.form.get("last_edited_by")
        
        # Validate required fields
        if not (servici and jo_no and date_in and make and model and color and posizione and received_by):
            flash("Please fill required fields", "danger")
            return redirect(url_for("home_blueprint.registro"))
        
        # Check duplicate JO number
        existing_registro = Registro.query.filter_by(jo_no=jo_no).first()
        if existing_registro:
            flash("J.O No. already exists.", "danger")
            return redirect(url_for("home_blueprint.registro"))
        
        # Check duplicate VIN
        existing_registro = Registro.query.filter_by(vin=vin).first()
        if existing_registro:
            flash("VIN already exists.", "danger")
            return redirect(url_for("home_blueprint.registro"))
        
        # Check duplicate Plate No
        existing_registro = Registro.query.filter_by(plate_no=plate_no).first()
        if existing_registro:
            flash("Plate No. already exists.", "danger")
            return redirect(url_for("home_blueprint.registro"))
        
        # Ensure Make/Model exist in Modelo table, else insert them
        existing_modelo = Modelo.query.filter_by(make=make, model=model).first()
        if not existing_modelo:
            new_modelo = Modelo(make=make, model=model)
            db.session.add(new_modelo)
            db.session.commit()

        # If unique, create new record
        new_registro = Registro(
            servici=servici, 
            jo_no=jo_no, 
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
            paperwork="No",
            diagnosis="PDD (Pending Diagnosis)", 
            estimate="Pending Estimate", 
            parts_and_materials="PPS (Parts Procurement Stage)", 
            billing="Pending Billing",  
            day_count=(datetime.today().date()-date_in).days, 
            checklist="None", 
            scartoffie="None", 
            transazioni="None", 
            transazioni_intl="None", 
            created=datetime.now(), 
            created_by=created_by, 
            last_edited=last_edited, 
            last_edited_by=last_edited_by
            )

        # Add to DB session
        db.session.add(new_registro)
        db.session.commit()

        flash("Successfully Added!", "success")
        return redirect(url_for("home_blueprint.registro"))

    # Query all registros from DB
    registro_data = Registro.query.all()

    modelo_data = Modelo.query.with_entities(Modelo.make, Modelo.model).distinct().all()

    # Convert to simple lists for dropdowns
    makes = sorted(set([m.make for m in modelo_data]))
    #models = sorted(set([m.model for m in modelo_data]))

    return render_template('home/registro.html', 
                           segment='registro', 
                           registro_data=registro_data,
                           makes=makes#,
                           #models=models
                           )

@blueprint.route('/registro/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_registro(id):
    registro = Registro.query.get_or_404(id)

    if request.method == "POST":

        # Convert dates safely
        date_in_str = request.form.get("date_in")
        date_out_str = request.form.get("date_out")
        date_checklisted_str = request.form.get("date_checklisted")
        created_str = request.form.get("created")
        last_edited_str = request.form.get("last_edited")

        registro.servici = request.form.get("servici")
        registro.jo_no = request.form.get("jo_no")
        registro.date_in = datetime.strptime(date_in_str, "%Y-%m-%d").date() if date_in_str else None
        registro.date_out = datetime.strptime(date_out_str, "%Y-%m-%d").date() if date_out_str else None
        registro.vin = request.form.get("vin")
        registro.make = request.form.get("make")
        registro.model = request.form.get("model")
        registro.plate_no = request.form.get("plate_no")
        registro.color = request.form.get("color")
        registro.notes = request.form.get("notes")
        registro.cliente = request.form.get("cliente")
        registro.tagged = request.form.get("tagged")
        registro.paperwork = request.form.get("paperwork")
        registro.diagnosis = request.form.get("diagnosis")
        registro.estimate = request.form.get("estimate")
        registro.parts_and_materials = request.form.get("parts_and_materials")
        registro.billing = request.form.get("billing")
        registro.posizione = request.form.get("posizione")
        registro.day_count = request.form.get("day_count")
        registro.released_to = request.form.get("released_to")
        registro.received_from = request.form.get("received_from")
        registro.related_jo = request.form.get("related_jo")
        registro.received_by = request.form.get("received_by")
        registro.date_checklisted = datetime.strptime(date_checklisted_str, "%Y-%m-%d").date() if date_checklisted_str else None
        registro.checklisted_by = request.form.get("checklisted_by")
        registro.released_by = request.form.get("released_by")
        registro.km_mileage = request.form.get("km_mileage")
        registro.concerns_requests = request.form.get("concerns_requests")
        registro.scartoffie = request.form.get("scartoffie")
        registro.transazioni = request.form.get("transazioni")
        registro.transazioni_intl = request.form.get("transazioni_intl")
        registro.created = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S") if created_str else datetime.now()
        registro.last_edited = datetime.strptime(last_edited_str, "%Y-%m-%d %H:%M:%S") if last_edited_str else datetime.now()
        registro.created_by = request.form.get("created_by")
        registro.last_edited_by = request.form.get("last_edited_by")
        registro.checklist = request.form.get("checklist")
        registro.onsite_details = request.form.get("onsite_details")

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
            flash("Updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating: " + str(e), "danger")

        return redirect(url_for("home_blueprint.registro"))

    #Pass makes for the dropdown in edit form too
    modelo_data = Modelo.query.with_entities(Modelo.make, Modelo.model).distinct().all()
    makes = sorted(set([m.make for m in modelo_data]))
    #models = sorted(set([m.model for m in modelo_data]))

    return render_template(
        "home/registro.html",
        segment="registro",
        registro=registro,
        makes=makes#,
        #models=models
    )

@blueprint.route('/registro/delete/<int:id>', methods=['POST'])
@login_required
def delete_registro(id):
    registro = Registro.query.get_or_404(id)

    try:
        db.session.delete(registro)
        db.session.commit()
        flash("Registro deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting registro: " + str(e), "danger")

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