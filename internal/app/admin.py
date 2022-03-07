from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask import Flask

from ..entity.application import Application
from .database import current_session
from .config import settings


app = Flask(__name__)
app.config.from_object(settings)

admin = Admin(
    app, url="/", name="Admin",
    template_mode="bootstrap4"
)
admin.add_view(ModelView(Application, current_session))
