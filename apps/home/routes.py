# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from apps.home.models import Customer
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound


@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')

# NEW: Customer View route
@blueprint.route('/customers')
@login_required
def customers():
    # Dummy data for now – replace with DB query later
    customer_data = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "phone": "09171234567"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "phone": "09181234567"}
    ]

    return render_template('home/customers.html', 
                           segment='customers', 
                           customers=customer_data)

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
