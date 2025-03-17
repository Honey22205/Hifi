from flask import Flask, flash, redirect, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

from sqlalchemy import MetaData

load_dotenv()

metadata = MetaData(
    naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
)

db=SQLAlchemy(metadata=metadata)

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
    
    # set up file upload folder
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    
    # change databse what we use
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    
    app.secret_key = os.getenv('SECRET_KEY')
    
    db.init_app(app)
    bcrypt = Bcrypt(app) # for hasing the password
    
    # login manager
    login_manager = LoginManager(app)
    login_manager.init_app(app)
    
    # models
    from models import Customer, Admin, DeliveryAgent
    @login_manager.user_loader
    def load_user(user_id):
        try:
            user_type, id_str = user_id.split(":")
            real_id = int(id_str)
        except Exception as e:
            # Return None if the id is not in the expected format
            return None

        if user_type == "customer":
            return Customer.query.get(real_id)
        elif user_type == "admin":
            return Admin.query.get(real_id)
        elif user_type == "delivery":
            return DeliveryAgent.query.get(real_id)
        return None

    
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        if '/admin' in request.path or '/delivery-agent' in request.path:
            flash('You are not authorized to access this page.', 'danger')
            return redirect(url_for('employee_login'))
        else:
            return redirect('/login')
    
    # mail
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_APP_PASSWORD')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mail = Mail(app)
    
    # routes 
    from routes.admin_routes import admin_routes
    from routes.delivery_agent_routes import delivery_agent_routes
    from routes.customer_routes import customer_routes
    from routes.auth_routes import register_routes
    
    register_routes(app, db, bcrypt, mail)
    admin_routes(app, db)
    delivery_agent_routes(app, db)
    customer_routes(app, db)
    
    
    
    migrate = Migrate(app, db)
    return app