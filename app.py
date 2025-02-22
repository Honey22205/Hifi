from flask import Flask, redirect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
    
    # change databse what we use
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    
    app.secret_key = os.getenv('SECRET_KEY')
    
    db.init_app(app)
    bcrypt = Bcrypt(app) # for hasing the password
    
    # login manager
    login_manager = LoginManager(app)
    login_manager.init_app(app)
    
    # models
    from models import Customer
    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))
    
    @login_manager.unauthorized_handler
    def unauthorized_callback(): # to handle the unauthorized access
        return redirect('/login')
    
    # routes 
    from routes import register_routes
    register_routes(app, db, Bcrypt)
    
    migrate = Migrate(app, db)
    return app