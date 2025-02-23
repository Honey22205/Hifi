from flask import Flask, render_template, request
from models import Customer
from flask_login import login_user, logout_user, current_user, login_required

def register_routes(app, db, bcrypt):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('home.html', user=current_user)
        else:
            return render_template('index.html')
        # return render_template('home.html')
       
    @app.route('/signup', methods=['POST', 'GET'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            address = request.form['address']
            new_user = Customer(username=username, email=email, phone=phone, password=hashed_password, address=address)
            db.session.add(new_user)
            db.session.commit()
            return render_template('index.html', user=current_user)
        else:
            return render_template('signup.html')
        
    @app.route('/login', methods=['POST', 'GET'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = Customer.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return render_template('home.html', user=current_user)
            else:
                return render_template('index.html', error='Invalid email or password')
        else:
            return render_template('index.html')