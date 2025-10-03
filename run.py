# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import click
from flask.cli import with_appcontext
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit

from apps.config import config_dict
from apps import create_app, db
from apps.scripts.import_modelo import import_modelo
from apps.scripts.import_registro import import_registro
from apps.scripts.auto_import import auto_upgrade

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT = ' + app_config.ASSETS_ROOT)

# ✅ Define CLI command OUTSIDE of function scope
@click.command("import-modelo")
@with_appcontext
def import_modelo_command():
    """Import vehicle data from CSV into Modelo table"""
    import_modelo()

# ✅ Define CLI command OUTSIDE of function scope
@click.command("import-registro")
@with_appcontext
def import_registro_command():
    """Import data from CSV into Registro table"""
    import_registro()

# ✅ Register the command
app.cli.add_command(import_modelo_command)
app.cli.add_command(import_registro_command)
app.cli.add_command(auto_upgrade)

if __name__ == "__main__":
    app.run()
