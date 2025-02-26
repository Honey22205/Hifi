import secrets
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from sqlalchemy import or_
from models import Customer, Admin, DeliveryAgent
from flask_login import login_user, logout_user, current_user, login_required

def register_routes(app, db, bcrypt, mail):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('home.html', user=current_user)  # Pass user data to frontend
        return render_template('login.html')  # Login page
    
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
                flash('Email already registered. Please log in.', 'error')
                return redirect(url_for('signup', message='Email already registered, please log in.'))

            # Create new user
            new_user = Customer(username=username, email=email, phone=phone, password=hashed_password, address=address)
            db.session.add(new_user)
            db.session.commit()

            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('index', message='Signup successful! Please log in.'))
        
        return render_template('signup.html')
        
    @app.route('/login', methods=['POST', 'GET'])
    def login():
        if request.method == 'POST':
            phone_email = request.form['phone-email']
            password = request.form['password']
            
            if '@' in phone_email:
                user = Customer.query.filter_by(email=phone_email).first()
            else:
                user = Customer.query.filter_by(phone=phone_email).first()

            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                session['user_id'] = user.id  # Store user ID in session
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login', message='Invalid phone or password'))

        return render_template('login.html')


    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.pop('user_id', None)  # Remove user session
        flash('Logged out successfully.', 'success')
        return redirect(url_for('index'))
    
    
    @app.route('/reset_password/<token>', methods=['POST', 'GET'])
    def reset_password(token):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['newPassword']
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = Customer.query.filter_by(email=email).first()
            if user:
                user.password = hashed_password
                db.session.commit()
                return redirect('/login')
            else:
                return render_template('forgetpwd.html', token=token)
        else:
            return render_template('forgetpwd.html', token=token)

    @app.route('/forget_password', methods=['POST', 'GET'])
    def forget_password():
        if request.method == 'POST':
            email = request.form.get('email')
            user = Customer.query.filter_by(email=email).first()

            if user:
                try:
                    reset_token = secrets.token_urlsafe(16)  
                    print(reset_token)
                    reset_link = url_for('reset_password', token=reset_token, _external=True)
                    print(reset_link)

                    msg = Message(
                        'Password Reset Request',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[email]
                    )
                    print(msg)
                    msg.body = f"""
                        Hello {user.username},

                        You requested to reset your password. Click the link below:

                        🔗 {reset_link}

                        If you did not request this, please ignore this email.

                        Thanks,  
                        HIFI Delivery Eats Team
                    """

                    mail.send(msg)
                    print('Mail sent successfully')

                    return jsonify({'success': True, 'message': 'Reset link sent successfully'})

                except Exception as e:
                    print(e)
                    return jsonify({'success': False, 'error': f'Error sending email: {str(e)}'})

            return jsonify({'success': False, 'error': 'Email not found'})

        return render_template('forgetemail.html')


    @app.route('/about')
    def about():
        return render_template('about.html')
    


    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    @app.route('/employee-login', methods=['GET', 'POST'])
    def employee_login():
        if request.method == 'POST':
            username = request.form['phone-email']
            password = request.form['password']
            role = request.form['role']  # "admin" or "delivery-agent"
            print(username, password, role)

            if role == 'admin':
                # Allow login using phone or email
                admin = Admin.query.filter(
                    or_(Admin.phone == username, Admin.email == username)
                ).first()
                print(admin)
                if admin and bcrypt.check_password_hash(admin.password, password):
                    login_user(admin)
                    return redirect(url_for('admin'))
                else:
                    return render_template('employee_login.html', message='Invalid username or password')
            
            elif role == 'delivery-agent':
                # Allow login using phone or email
                delivery_agent = DeliveryAgent.query.filter(
                    or_(DeliveryAgent.phone == username, DeliveryAgent.email == username)
                ).first()
                if delivery_agent and bcrypt.check_password_hash(delivery_agent.password, password):
                    login_user(delivery_agent)
                    return redirect(url_for('delivery_agent'))
                else:
                    return render_template('employee_login.html', message='Invalid username or password')    
            
            else:
                return render_template('employee_login.html', message='Invalid role')
        
        else:
            return render_template('employee_login.html')
        
    @app.route('/employee-signup', methods=['POST'])
    def employee_signup():
        # Support both JSON payload and form-data
        data = request.get_json() if request.is_json else request.form

        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        # Validate required fields
        if not all([phone, email, password, username]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Validate and convert phone to int if needed
        try:
            phone_int = int(phone)
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid phone number format'}), 400

        # Hash password using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check if an admin with the same email or phone already exists
        existing_admin = Admin.query.filter(
            or_(Admin.email == email, Admin.phone == phone_int)
        ).first()
        if existing_admin:
            return jsonify({'success': False, 'error': 'Email or phone number already registered'}), 400

        # Create new admin user
        new_admin = Admin(
            username=username,
            email=email,
            phone=phone_int,
            password=hashed_password
        )
        
        try:
            db.session.add(new_admin)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Database error occurred', 'message': str(e)}), 500

        return jsonify({'success': True, 'message': 'Signup successful!'}), 201


def admin_routes(app, db):
    @app.route('/admin')
    def admin():
        return render_template('admin/home.html')
    