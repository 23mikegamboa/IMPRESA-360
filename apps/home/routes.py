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


@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')

# NEW: Customer view & add route
@blueprint.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():

    if request.method == "POST":
        # Get form inputs

         # Convert to Python date objects (if provided)
        date_in_str = request.form.get("date_in")
        date_out_str = request.form.get("date_out")
        date_checklisted_str = request.form.get("date_checklisted")
        created_str = request.form.get("created")
        last_edited_str = request.form.get("last_edited")

        #name = request.form.get("name")
        servici = request.form.get("servici")
        jo_no = request.form.get("jo_no")
        #date_in = request.form.get("date_in").strftime("%m/%d/%Y")
        #date_out = request.form.get("date_out").strftime("%m/%d/%Y")
        #date_in = request.form.get("date_in")
        #date_out = request.form.get("date_out")
        date_in = datetime.strptime(date_in_str, "%Y-%m-%d").date() if date_in_str else None
        date_out = datetime.strptime(date_out_str, "%Y-%m-%d").date() if date_out_str else None
        vin = request.form.get("vin")
        make = request.form.get("make")
        model = request.form.get("model")
        plate_no = request.form.get("plate_no")
        color = request.form.get("color")
        notes = request.form.get("notes")
        cliente = request.form.get("cliente")
        tagged = request.form.get("tagged")
        paperwork = request.form.get("paperwork")
        diagnosis = request.form.get("diagnosis")
        estimate = request.form.get("estimate")
        parts_and_materials = request.form.get("parts_and_materials")
        billing = request.form.get("billing")
        posizione = request.form.get("posizione")
        day_count = request.form.get("day_count")
        released_to = request.form.get("released_to")
        received_from = request.form.get("received_from")
        related_jo = request.form.get("related_jo")
        received_by = request.form.get("received_by")
        #date_checklisted = request.form.get("date_checklisted")
        date_checklisted = datetime.strptime(date_checklisted_str, "%Y-%m-%d").date() if date_checklisted_str else None
        checklisted_by = request.form.get("checklisted_by")
        released_by = request.form.get("released_by")
        km_mileage = request.form.get("km_mileage")
        concerns_requests = request.form.get("concerns_requests")
        scartoffie = request.form.get("scartoffie")
        transazioni = request.form.get("transazioni")
        #created = request.form.get("created")
        created = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S") if created_str else datetime.now()
        #last_edited = request.form.get("last_edited")
        last_edited = datetime.strptime(last_edited_str, "%Y-%m-%d %H:%M:%S") if last_edited_str else datetime.now()
        created_by = request.form.get("created_by")
        last_edited_by = request.form.get("last_edited_by")
        checklist = request.form.get("checklist")
        onsite_details = request.form.get("onsite_details")
        
        # Validate required fields
        if not (servici and jo_no and date_in and vin and make and model and plate_no and color and cliente and posizione and received_by):
            flash("Please fill required fields", "danger")
            return redirect(url_for("home_blueprint.registro"))
        
        # Check duplicate JO number
        existing_registro = Registro.query.filter_by(jo_no=jo_no).first()
        if existing_registro:
            flash("J.O No. already exists.", "danger")
            return redirect(url_for("home_blueprint.registro"))
        
        # Ensure Make/Model exist in Modelo table, else insert them
        existing_modelo = Modelo.query.filter_by(make=make, model=model).first()
        if not existing_modelo:
            new_modelo = Modelo(make=make, model=model)
            db.session.add(new_modelo)
            db.session.commit()

        # If unique, create new record
        new_registro = Registro(servici=servici, jo_no=jo_no, date_in=date_in, date_out=date_out, vin=vin, make=make, model=model, plate_no=plate_no, color=color, notes=notes, cliente=cliente, tagged=tagged, paperwork=paperwork, diagnosis=diagnosis, estimate=estimate, parts_and_materials=parts_and_materials, billing=billing, posizione=posizione, day_count=day_count, released_to=released_to, received_from=received_from, related_jo=related_jo, received_by=received_by, date_checklisted=date_checklisted, checklisted_by=checklisted_by, released_by=released_by, km_mileage=km_mileage, concerns_requests=concerns_requests, scartoffie=scartoffie, transazioni=transazioni, created=created, last_edited=last_edited, created_by=created_by, last_edited_by=last_edited_by, checklist=checklist, onsite_details=onsite_details)

        # Add to DB session
        db.session.add(new_registro)
        db.session.commit()

        flash("Successfully Added!", "success")
        return redirect(url_for("home_blueprint.registro"))

    # Query all registros from DB
    registro_data = Registro.query.all()
    #modelo_data = Modelo.query.with_entities(Modelo.make, Modelo.model).distinct().all()

    modelo_data = Modelo.query.with_entities(Modelo.make).distinct().all()

    # Convert to simple lists for dropdowns
    makes = sorted(set([m.make for m in modelo_data]))

    return render_template('home/registro.html', 
                           segment='registro', 
                           registro_data=registro_data,
                           makes=makes)

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

        #registro.name = request.form.get("name")
        registro.servici = request.form.get("servici")
        registro.jo_no = request.form.get("jo_no")
        #registro.date_in = request.form.get("date_in").strftime("%m/%d/%Y")
        #registro.date_out = request.form.get("date_out").strftime("%m/%d/%Y")
        #registro.date_in = request.form.get("date_in")
        #registro.date_out = request.form.get("date_out")
        registro.date_in = datetime.strptime(date_in_str, "%Y-%m-%d").date() if date_in_str else None
        registro.date_out = datetime.strptime(date_out_str, "%Y-%m-%d").date() if date_out_str else None
        registro.vin = request.form.get("vin")
        registro.make = request.form.get("make")
        registro.model = request.form.get("model")
        registro.plate_no = request.form.get("plate_no")
        registro.color = request.form.get("color")
        registro.notes = request.form.get("notes")
        registro.cliente = request.form.get("cliente")
        registro.tagged = bool(request.form.get("tagged"))
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
        #registro.date_checklisted = request.form.get("date_checklisted").strftime("%m/%d/%Y")
        registro.date_checklisted = datetime.strptime(date_checklisted_str, "%Y-%m-%d").date() if date_checklisted_str else None
        registro.checklisted_by = request.form.get("checklisted_by")
        registro.released_by = request.form.get("released_by")
        registro.km_mileage = request.form.get("km_mileage")
        registro.concerns_requests = request.form.get("concerns_requests")
        registro.scartoffie = request.form.get("scartoffie")
        registro.transazioni = request.form.get("transazioni")
        #registro.created = request.form.get("created")
        registro.created = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S") if created_str else datetime.now()
        #registro.last_edited = request.form.get("last_edited")
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
            flash("Registro updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating registro: " + str(e), "danger")

        return redirect(url_for("home_blueprint.registro"))

    #Pass makes for the dropdown in edit form too
    modelo_data = Modelo.query.with_entities(Modelo.make, Modelo.model).distinct().all()
    makes = sorted(set([m.make for m in modelo_data]))

    return render_template(
        "home/edit_registro.html",
        segment="registro",
        registro=registro,
        makes=makes
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
        .all()
    )
    # Return list of model names (filter out None just in case)
    return jsonify([m.model for m in models if m.model])
