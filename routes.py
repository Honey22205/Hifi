from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import Customer
from flask_login import login_user, logout_user, current_user, login_required

def register_routes(app, db, bcrypt):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('home.html', user=current_user)  # Pass user data to frontend
        return render_template('index.html')  # Login page
    
    @app.route('/signup', methods=['POST', 'GET'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            address = request.form['address']

            # Hash password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Check if user already exists
            if Customer.query.filter_by(email=email).first():
                # flash('Email already registered. Please log in.', 'error')
                return redirect(url_for('index', message='Email already registered, please log in.'))

            # Create new user
            new_user = Customer(username=username, email=email, phone=phone, password=hashed_password, address=address)
            db.session.add(new_user)
            db.session.commit()

            # flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('index', message='Signup successful! Please log in.'))
        
        return render_template('signup.html')
        
    @app.route('/login', methods=['POST', 'GET'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = Customer.query.filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                session['user_id'] = user.id  # Store user ID in session
                # flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                # flash('Invalid email or password', 'error')
                return redirect(url_for('login', message='Invalid email or password'))

        return render_template('index.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.pop('user_id', None)  # Remove user session
        # flash('Logged out successfully.', 'success')
        return redirect(url_for('index'))
