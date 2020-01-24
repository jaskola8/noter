import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask.cli import with_appcontext
from flask_talisman import Talisman
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
import click
import datetime

db = SQLAlchemy()
csrf = CSRFProtect()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/main.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SECRET_KEY"] = b'2B\x0c\xac\xfa$\r[\xbd8\xbb}wXg\xd1'
    app.config['REMEMBER_COOKIE_DURATION'] = datetime.timedelta(hours=8)
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    login_manager.session_protection = "strong"

    db.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = "strong"
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.cli.add_command(init_db_command)
    from app.notes.views import notes
    from app.auth.views import auth
    from app.notes.views import index
    app.register_blueprint(notes, url_prefix="/notes")
    app.register_blueprint(auth)
    app.add_url_rule("/", 'index', index)
    return app


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.drop_all()
    db.create_all()
    from app.notes.models import initialize_notes
    from app.auth.models import initialize_users
    click.echo("Initializing users")
    initialize_users()
    click.echo("Initializing notes")
    initialize_notes()
    click.echo("DB Initialized")


app = create_app()
