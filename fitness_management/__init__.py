from flask import Flask
from .user.routes import user_bp
from .workout_planner.routes import workout_bp
from .database import db
import ast


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SECRET_KEY"] = "dskjdhskdhshdkshdksjh"
app.register_blueprint(user_bp, url_prefix='/')
app.register_blueprint(workout_bp, url_prefix='/')


db.init_app(app)
with app.app_context():
    db.create_all()
