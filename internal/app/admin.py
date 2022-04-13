from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from internal.config import settings
from internal.config.database import current_session
from internal.entity.application import Application


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(settings)

    admin = Admin(
        app=app,
        url='/',
        name='Admin',
        template_mode='bootstrap4',
    )
    admin.add_view(ModelView(Application, current_session))

    return app
