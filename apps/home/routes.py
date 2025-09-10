# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from apps.home.models import Registro
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import db


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
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")

        if not (name and email and phone):
            flash("All fields are required.", "danger")
            return redirect(url_for("home_blueprint.registro"))
            
        existing = Registro.query.filter_by(email=email).first()
        if existing:
            flash("Email already exists. Please use a different one.", "danger")
            return redirect(url_for("home_blueprint.registro"))
            
        # If unique, create new record
        new_registro = Registro(name=name, email=email, phone=phone)

        # Add to DB session
        db.session.add(new_registro)
        db.session.commit()

        flash("New registro added successfully!", "success")
        #return redirect(url_for("home.registro"))
        return redirect(url_for("home_blueprint.registro"))

    # Query all registros from DB
    registro_data = Registro.query.all()

    return render_template('home/registro.html', 
                           segment='registro', 
                           registro=registro_data)

@blueprint.route('/registro/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_registro(id):
    registro = Registro.query.get_or_404(id)

    if request.method == "POST":
        registro.name = request.form.get("name")
        registro.email = request.form.get("email")
        registro.phone = request.form.get("phone")

        try:
            db.session.commit()
            flash("Registro updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating registro: " + str(e), "danger")

        return redirect(url_for("home_blueprint.registro"))

    return render_template("home/edit_registro.html",
                           segment="registro",
                           registro=registro)

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
