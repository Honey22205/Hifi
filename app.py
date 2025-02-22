from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
    
    # change databse what we use
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    
    app.secret_key = os.getenv('SECRET_KEY')
    
    db.init_app(app)
    
    migrate = Migrate(app, db)
    return app