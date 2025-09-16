from flask_migrate import upgrade
from flask.cli import with_appcontext
import click
from apps.scripts.import_modelo import import_modelo

@click.command("auto-upgrade")
@with_appcontext
def auto_upgrade():
    """Run migrations and import Modelo CSV in one step."""
    # Step 1: Run migrations
    upgrade()
    # Step 2: Import Modelo CSV
    import_modelo()
    click.echo("✅ Database upgraded and Modelo imported from MODELO_UPDATED.csv")
