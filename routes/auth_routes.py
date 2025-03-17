import secrets
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from sqlalchemy import or_

from models import Address, Admin, Customer, DeliveryAgent


def register_routes(app, db, bcrypt, mail):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('home.html', user=current_user)  # Pass user data to frontend
        return render_template('login.html')  # Login page
    
    @app.route('/signup', methods=['POST', 'GET'])
    def signup():
        if request.method == 'POST':
            # print("DEBUG: Form Data Received ->", request.form)  

            username = request.form.get('username')
            email = request.form.get('email')
            phone = request.form.get('phone')
            password = request.form.get('password')

            address_line = request.form.get('address_line')
            city = request.form.get('city')
            state = request.form.get('state')
            zip_code = request.form.get('zip_code')

            if not all([username, email, phone, password, address_line, city, state, zip_code]):
                flash('All fields are required.', 'error')
                return redirect(url_for('signup'))

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            if Customer.query.filter_by(email=email).first():
                flash('Email already registered. Please log in.', 'error')
                return redirect(url_for('signup'))
            
            if Customer.query.filter_by(phone=phone).first():
                flash('Phone number already registered. Please log in.', 'error')
                return redirect(url_for('signup'))

            # Create new customer entry
            new_customer = Customer(username=username, email=email, phone=phone, password=hashed_password)
            db.session.add(new_customer)
            db.session.commit()  # Commit first to get `id` for address
            
            # Add Address Entry
            new_address = Address(
                customer_id=new_customer.id,  # Use the newly created customer's ID
                address_line=address_line,
                city=city,
                state=state,
                zip_code=zip_code,
                is_preferred=True
            )
            db.session.add(new_address)
            db.session.commit()
            
            # Send welcome email
            try:
                msg = Message(
                    "Welcome to HIFI Delivery Eats!",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email]
                )
                msg.body = f"""
                    Hello {username},

                    Thank you for signing up for HIFI Delivery Eats!

                    Your registered email: {email}
                    Your registered phone: {phone}

                    We are excited to have you on board.

                    Regards,  
                    HIFI Delivery Eats Team
                """
                mail.send(msg)
                print("Welcome email sent successfully.")
            except Exception as e:
                print(f"Error sending email: {e}")

            flash('Signup successful!', 'success')
            return redirect(url_for('index'))

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
                    # print(reset_token)
                    reset_link = url_for('reset_password', token=reset_token, _external=True)
                    # print(reset_link)

                    msg = Message(
                        'Password Reset Request',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[email]
                    )
                    # print(msg)
                    msg.body = f"""
                        Hello {user.username},

                        You requested to reset your password. Click the link below:

                        🔗 {reset_link}

                        If you did not request this, please ignore this email.

                        Thanks,  
                        HIFI Delivery Eats Team
                    """

                    mail.send(msg)
                    # print('Mail sent successfully')

                    return jsonify({'success': True, 'message': 'Reset link sent successfully'})

                except Exception as e:
                    # print(e)
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
            # print(username, password, role)

            if role == 'admin':
                # Allow login using phone or email
                admin = Admin.query.filter(
                    or_(Admin.phone == username, Admin.email == username)
                ).first()
                # print(admin)
                if admin and bcrypt.check_password_hash(admin.password, password):
                    login_user(admin)
                    # print("Login successful")
                    session['user_id'] = admin.id  # Store user ID in session
                    db.session.refresh(current_user)
                    return redirect(url_for('admin'))
                else:
                    flash('Invalid username or password')
                    return render_template('employee_login.html', message='Invalid username or password')
            
            elif role == 'delivery-agent':
                # Allow login using phone or email
                delivery_agent = DeliveryAgent.query.filter(
                    or_(DeliveryAgent.phone == username, DeliveryAgent.email == username)
                ).first()
                if delivery_agent:
                    # Check if the account is approved and active
                    if not (delivery_agent.is_approved and delivery_agent.is_active):
                        flash('Your account is either not approved or inactive. Please contact support.')
                        return render_template('employee_login.html', message='Your account is either not approved or inactive.')
                    # Check password
                    if bcrypt.check_password_hash(delivery_agent.password, password):
                        login_user(delivery_agent)
                        db.session.refresh(current_user)
                        print(current_user.get_id())
                        return redirect(url_for('delivery_agent'))
                    else:
                        flash('Invalid username or password')
                        return render_template('employee_login.html', message='Invalid username or password')
                else:
                    flash('Invalid username or password')
                    return render_template('employee_login.html', message='Invalid username or password')
            
            else:
                flash('Invalid role')
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
    
    @app.route('/employee-logout')
    @login_required
    def employee_logout():
        logout_user()
        session.pop('user_id', None)
        flash('Logged out successfully.', 'success')
        return redirect(url_for('employee_login'))
    
    
    @app.route('/delivery_signup', methods=['POST', 'GET'])
    def delivery_signup():
        if request.method == 'POST':
            phone = request.form['phone']
            email = request.form['email']
            password = request.form['password']
            username = request.form['username']
            delivery_area = request.form['delivery_area']
            id_proof = request.form['id_proof']
            
            # Validate required fields
            if not all([phone, email, password, username, delivery_area]):
                flash('Please enter all required fields')
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            # Validate and convert phone to int if needed
            try:
                phone_int = int(phone)
            except ValueError:
                flash('Invalid phone number format')
                return jsonify({'success': False, 'error': 'Invalid phone number format'}), 400
            
            # Hash password using bcrypt
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Check if a delivery agent with the same email or phone already exists
            existing_delivery_agent = DeliveryAgent.query.filter(
                or_(DeliveryAgent.email == email, DeliveryAgent.phone == phone_int)
            ).first()
            if existing_delivery_agent:
                flash('Email or phone number already registered')
                return render_template('delivery_agent_signup.html')
            
            # Create new delivery agent user
            new_delivery_agent = DeliveryAgent(
                username=username,
                email=email,
                phone=phone_int,
                password=hashed_password,
                delivery_area=delivery_area,
                id_proof=id_proof
            )
            
            try:
                db.session.add(new_delivery_agent)
                db.session.commit()
                flash('Signup successful! Your request is sended to administrator')
                return redirect('employee-login')
            except Exception as e:
                db.session.rollback()
                flash('Database error occurred')
                return jsonify({'success': False, 'error': 'Database error occurred', 'message': str(e)}), 500
        else:
            return render_template('delivery_agent_signup.html')
            
