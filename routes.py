import datetime
import os
import secrets
from zoneinfo import ZoneInfo
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_mail import Message
from sqlalchemy import func, or_
from models import Customer, Admin, DeliveryAgent, Address, Order, OrderItem, MenuItem
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

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
            



# Admin routes
def admin_routes(app, db):
    @app.route('/admin')
    def admin():
        if not current_user.is_authenticated:
            return redirect(url_for('employee_login'))
        
        return render_template('admin/home.html')

    
    @app.route('/admin/delivery_partner')
    @login_required
    def delivery_partner():
        pending_agents = DeliveryAgent.query.filter_by(is_approved=False).all()
        accepted_agents = DeliveryAgent.query.filter_by(is_approved=True).all()
        return render_template(
            'admin/delivery_partner.html',
            pending_agents=pending_agents,
            accepted_agents=accepted_agents
        )
    
    @app.route('/admin/accept/<int:id>', methods=['POST'])
    def accept_agent(id):
        agent = DeliveryAgent.query.get(id)
        if not agent:
            flash("Agent not found")
            return jsonify({"message": "Agent not found"}), 404
        agent.is_approved = True  # Set approval status
        db.session.commit()
        
        flash(f"Agent {agent.username} accepted!")
        return jsonify({"message": f"Agent {agent.username} accepted!"})
    

    @app.route('/admin/reject/<int:id>', methods=['POST'])
    def reject_agent(id):
        agent = DeliveryAgent.query.get(id)
        if not agent:
            flash("Agent not found")
            return jsonify({"message": "Agent not found"}), 404

        # Delete the agent from the database
        db.session.delete(agent)
        db.session.commit()
        
        flash(f"Agent {agent.username} has been rejected and removed from the database!")

        return jsonify({"message": f"Agent {agent.username} has been rejected and removed from the database!"})
    
    @app.route('/admin/deactivate/<int:id>', methods=['POST'])
    def deactivate_agent(id):
        agent = DeliveryAgent.query.get(id)
        if not agent:
            flash("Agent not found")
            return jsonify({"message": "Agent not found"}), 404
        agent.is_active = False
        db.session.commit()
        flash(f"Agent {agent.username} has been deactivated.")
        return jsonify({"message": f"Agent {agent.username} has been deactivated."})

    @app.route('/admin/activate/<int:id>', methods=['POST'])
    def activate_agent(id):
        agent = DeliveryAgent.query.get(id)
        if not agent:
            flash("Agent not found")
            return jsonify({"message": "Agent not found"}), 404
        agent.is_active = True
        db.session.commit()
        flash(f"Agent {agent.username} has been activated.")
        return jsonify({"message": f"Agent {agent.username} has been activated."})




    
# Customer routes
def customer_routes(app, db):
    @app.route('/user/profile')
    @login_required
    def customer():
        return render_template('user/profile.html', user=current_user)

    @app.route("/address/new", methods=["POST"])
    @login_required
    def add_address():
        data = request.get_json()
        new_address = Address(
            address_line=data.get("address_line"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            customer_id=current_user.id
        )
        db.session.add(new_address)
        db.session.commit()
        return jsonify({"message": "Address added successfully!"}), 201
    

    @app.route("/address/<int:address_id>/set-preferred", methods=["POST"])
    @login_required
    def set_preferred_address(address_id):
        # Fetch the selected address
        address = Address.query.filter_by(id=address_id, customer_id=current_user.id).first()
        
        if not address:
            return jsonify({"error": "Address not found"}), 404

        # Set all addresses to "not preferred"
        Address.query.filter_by(customer_id=current_user.id).update({"is_preferred": False})

        # Set the selected address as preferred
        address.is_preferred = True
        db.session.commit()

        return jsonify({"message": "Default address updated!"}), 200
    
    @app.route("/address/<int:address_id>", methods=["DELETE"])
    @login_required
    def delete_address(address_id):
        # Fetch the address
        address = Address.query.filter_by(id=address_id, customer_id=current_user.id).first()

        if not address:
            return jsonify({"error": "Address not found"}), 404

        # Delete the address from the database
        db.session.delete(address)
        db.session.commit()

        return jsonify({"message": "Address deleted successfully!"}), 200


    # @app.route("/address/<int:address_id>", methods=["PUT"])
    # @login_required
    # def edit_address(address_id):
    #     data = request.get_json()
    #     address = Address.query.filter_by(id=address_id, customer_id=current_user.id).first()
        
    #     if not address:
    #         return jsonify({"error": "Address not found"}), 404

    #     # Update only if values are provided and not empty
    #     if data.get("address_line"):
    #         address.address_line = data["address_line"]
    #     if data.get("city"):
    #         address.city = data["city"]
    #     if data.get("state"):
    #         address.state = data["state"]
    #     if data.get("zip_code"):
    #         address.zip_code = data["zip_code"]

    #     db.session.commit()
        
    #     return jsonify({
    #         "message": "Address updated successfully!",
    #         "address": {
    #             "address_line": address.address_line,
    #             "city": address.city,
    #             "state": address.state,
    #             "zip_code": address.zip_code
    #         }
    #     }), 200





# Delivery agent routes
def delivery_agent_routes(app, db):
    @app.route('/delivery-agent')
    def delivery_agent():
        # Get the delivery agent using the current user's ID
        agent = DeliveryAgent.query.get(current_user.id)
        
        # Create a subquery that selects one address per customer
        address_subquery = (
            db.session.query(
                Address.customer_id,
                func.min(Address.address_line).label("customer_address")
            )
            .group_by(Address.customer_id)
            .subquery()
        )

        pending_orders = (
            db.session.query(
                Order.id.label("order_id"),
                Customer.id.label("customer_id"),
                Customer.username.label("customer_name"),
                Customer.phone.label("customer_phone"),
                address_subquery.c.customer_address,
                Order.status.label("order_status"),
                Order.total_price.label("order_total"),
                Order.delivery_location.label("delivery_location"),
                Order.created_at.label("order_date"),
            )
            .join(Customer, Order.user_id == Customer.id)
            .outerjoin(address_subquery, address_subquery.c.customer_id == Customer.id)
            .filter(Order.delivery_agent_id == current_user.id, Order.status == "Pending")
            .all()
        )

        
        # Query assigned orders (orders with status "Accepted")
        assigned_orders = (
            db.session.query(
                Order.id.label("order_id"),
                Customer.id.label("customer_id"),
                Customer.username.label("customer_name"),
                Customer.phone.label("customer_phone"),
                Address.address_line.label("customer_address"),
                Order.status.label("order_status"),
                Order.total_price.label("order_total"),
                Order.delivery_location.label("delivery_location"),
                Order.created_at.label("order_date"),
            )
            .join(Customer, Order.user_id == Customer.id)
            .outerjoin(Address, Address.customer_id == Customer.id)
            .filter(Order.delivery_agent_id == current_user.id, Order.status == "Accepted")
            .group_by(Order.id, Customer.id)
            .all()
        )
        
        # Query completed orders
        completed_orders = (
            db.session.query(
                Order.id.label("order_id"),
                Customer.id.label("customer_id"),
                Customer.username.label("customer_name"),
                Customer.phone.label("customer_phone"),
                Address.address_line.label("customer_address"),
                Order.delivery_status.label("order_status"),
                Order.total_price.label("order_total"),
                Order.delivery_location.label("delivery_location"),
                Order.created_at.label("order_date"),
            )
            .join(Customer, Order.user_id == Customer.id)
            .outerjoin(Address, Address.customer_id == Customer.id)
            .filter(Order.delivery_agent_id == current_user.id, Order.delivery_status == "Delivered")
            .group_by(Order.id, Customer.id)
            .all()
        )
        
        # Define today's date using Indian Standard Time (IST)
        today = datetime.datetime.now()
        
        # Count today's delivered orders (assuming 'Delivered' status marks a completed delivery)
        todays_deliveries_count = (
            db.session.query(Order)
            .filter(
                Order.delivery_agent_id == current_user.id,
                db.func.date(Order.created_at) == today,
                Order.status == "Delivered"  # Adjust if your status differs
            )
            .count()
        )
        
        # Count total pending orders for the delivery agent
        pending_count = (
            db.session.query(Order)
            .filter(Order.delivery_agent_id == current_user.id, Order.status == "Pending")
            .count()
        )
        
        # Count total completed orders for the delivery agent
        completed_count = (
            db.session.query(Order)
            .filter(Order.delivery_agent_id == current_user.id, Order.delivery_status == "Delivered")
            .count()
        )
        
        print(pending_orders)
        
        # Pass all the data to the template
        return render_template(
            'delivery_agent/dashboard.html',
            user=agent,
            pending_orders=pending_orders,
            assigned_orders=assigned_orders,
            completed_orders=completed_orders,
            todays_deliveries_count=todays_deliveries_count,
            pending_count=pending_count,
            completed_count=completed_count,
            timedelta=datetime.timedelta
        )
    




    @app.route('/delivery-partner/profile')
    def delivery_partner_profile():
        # Ensure the user is authenticated.
        if not current_user.is_authenticated:
            flash("Please log in to access your profile.", "danger")
            return redirect(url_for('employee_login'))
        
        # Fetch the latest delivery agent data from the database
        agent = DeliveryAgent.query.get(current_user.id)
        print("Loaded agent:", agent)
        return render_template('delivery_agent/profile.html', user=agent)
    




    @app.route('/delivery-partner/order-detail/<int:order_id>')
    def delivery_partner_order_detail(order_id):
        """Fetch detailed order information along with order items and customer details."""
        
        order = (
            db.session.query(Order)
            .options(
                joinedload(Order.user).joinedload(Customer.addresses),  # Load customer's addresses
                joinedload(Order.items).joinedload(OrderItem.menu_item)  # Load each order item's menu details
            )
            .filter(
                Order.delivery_agent_id == current_user.id,
                Order.id == order_id
            )
            .first()
        )
        
        if not order:
            return "Order not found", 404
        
        return render_template("delivery_agent/order_detail.html", user=current_user, order=order)



    @app.route('/order/<int:order_id>/accept', methods=['POST'])
    @login_required
    def accept_order(order_id):
        order = Order.query.get_or_404(order_id)
        
        # Ensure order is pending and not already assigned
        if order.status != "Pending":
            flash("Order Already accepted.")
            return redirect(url_for("delivery_agent"))
        
        order.status = "Accepted"
        order.delivery_agent_id = current_user.id  # Assign to the logged-in delivery agent
        db.session.commit()
        
        # return render_template("delivery_agent/order_detail.html")
        flash("Order Accepted successfully")
        return redirect(url_for('delivery_agent'))

    @app.route('/order/<int:order_id>/decline', methods=['POST'])
    @login_required
    def decline_order(order_id):
        order = Order.query.get_or_404(order_id)
        
        # Ensure order is pending before declining
        if order.status != "Pending":
            flash("Order Already declined.")
            return redirect(url_for("delivery_agent"))
        
        order.status = "Declined"
        order.delivery_agent_id = None  # Unassign from the logged-in delivery agent if available.
        db.session.commit()
        
        flash("Order declined successfully")
        return redirect(url_for("delivery_agent"))



    @app.route('/delivery_status/<int:order_id>/edit', methods=['POST'])
    def edit_delivery_status(order_id):
        order = Order.query.get_or_404(order_id)
        
        valid_statuses = ["Order Pickup", "On the Way", "Reached Destination", "Delivered" ]
        new_status = request.form.get('delivery_status')
        
        if new_status in valid_statuses:
            order.delivery_status = new_status
            if new_status == "Delivered":
                order.delivered_at = func.now()
            db.session.commit()
        else:
            return "Invalid status update", 400
        
        return redirect(url_for('delivery_agent'))
    



    @app.route('/delivery_agent/<int:agent_id>/edit', methods=['POST'])
    def edit_delivery_agent(agent_id):
        # Get the delivery agent or return 404 if not found.
        agent = DeliveryAgent.query.get_or_404(agent_id)
        
        # Update text fields with submitted values or fallback to existing ones.
        agent.username = request.form.get('username', agent.username)
        agent.email = request.form.get('email', agent.email)
        
        phone = request.form.get('phone')
        if phone:
            try:
                agent.phone = int(phone)
            except ValueError:
                flash("Invalid phone number.", "danger")
                return redirect(url_for('delivery_partner_profile'))
        agent.delivery_area = request.form.get('delivery_area', agent.delivery_area)
        agent.id_proof = request.form.get('id_proof', agent.id_proof)
        agent.bio = request.form.get('bio', agent.bio)
        
        # Update checkbox field.
        agent.available_slots = True if request.form.get('available_slots') == 'on' else False

        # Handle file upload.
        file = request.files.get('image')
        if  file and file.filename:
            filename = secure_filename(file.filename)
            # Save the file to the upload folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Construct the relative path to store in the database
            relative_path = os.path.join('uploads', filename).replace(os.sep, '/')
            agent.image = relative_path


        try:
            db.session.commit()
            flash("Delivery agent details updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating details: {e}", "danger")
        
        # Redirect to the profile page which fetches the latest data.
        return redirect(url_for('delivery_partner_profile'))
    
    
    
#     @app.route('/api/orders/<int:order_id>/complete', methods=['POST'])
#     @login_required
#     def complete_order(order_id):
#         order = Order.query.get_or_404(order_id)
#         order.status = 'Completed'
#         order.delivered_at = func.now()
        
#         # Update or create earnings record for today
#         today_earnings = Earnings.query.filter(
#             Earnings.delivery_agent_id == current_user.id,
#             func.date(Earnings.earned_at) == func.date(func.now())
#         ).first()
        
#         base_pay_per_delivery = 50.0
        
#         if today_earnings:
#             # Add base pay for this delivery
#             today_earnings.base_pay += base_pay_per_delivery
#             today_earnings.trips_count += 1
#             # Add bonus for every 5 trips
#             if today_earnings.trips_count % 5 == 0:
#                 today_earnings.bonus += 100.0
#         else:
#             # Get previous earnings to carry forward
#             previous_earnings = Earnings.query.filter(
#                 Earnings.delivery_agent_id == current_user.id,
#                 func.date(Earnings.earned_at) < func.date(func.now())
#             ).order_by(Earnings.earned_at.desc()).first()
            
#             initial_base_pay = previous_earnings.base_pay if previous_earnings else 0.0
#             initial_bonus = previous_earnings.bonus if previous_earnings else 0.0
            
#             today_earnings = Earnings(
#                 delivery_agent_id=current_user.id,
#                 base_pay=initial_base_pay + base_pay_per_delivery,
#                 bonus=initial_bonus,
#                 trips_count=1
#             )
#             db.session.add(today_earnings)
        
#         db.session.commit()
#         return jsonify({'message': 'Order completed successfully', 'earnings': {
#             'base_pay': today_earnings.base_pay,
#             'bonus': today_earnings.bonus,
#             'trips_count': today_earnings.trips_count,
#             'total': today_earnings.base_pay + today_earnings.bonus
#         }})

#     @app.route('/api/delivery-agent/earnings')
#     @login_required
#     def get_current_earnings():
#         today_earnings = Earnings.query.filter(
#             Earnings.delivery_agent_id == current_user.id,
#             func.date(Earnings.earned_at) == func.date(func.now())
#         ).first()

#         if not today_earnings:
#             return jsonify({
#                 'base_pay': 0.0,
#                 'bonus': 0.0,
#                 'trips_count': 0
#             })

#         return jsonify({
#             'base_pay': today_earnings.base_pay,
#             'bonus': today_earnings.bonus,
#             'trips_count': today_earnings.trips_count
#         })
    
#     @app.route('/delivery-agent/earnings/<int:agent_id>')
#     @login_required
#     def get_agent_earnings(agent_id):
#         # Query earnings for the specific delivery agent
#         earnings = Earnings.query.filter_by(delivery_agent_id=agent_id).all()
        
#         # Format the earnings data
#         earnings_data = [{
#             'base_pay': earning.base_pay,
#             'bonus': earning.bonus,
#             'trips_count': earning.trips_count,
#             'earned_at': earning.earned_at.strftime('%Y-%m-%d %H:%M:%S'),
#             'total': earning.base_pay + earning.bonus
#         } for earning in earnings]
        
#         return jsonify(earnings_data)


# # Customer routes
# def customer_routes(app, db):
#     @app.route('/user/profile')
#     @login_required
#     def customer():
#         return render_template('user/profile.html', user=current_user)

#     @app.route("/address/new", methods=["POST"])
#     @login_required
#     def add_address():
#         data = request.get_json()
#         new_address = Address(
#             address_line=data.get("address_line"),
#             city=data.get("city"),
#             state=data.get("state"),
#             zip_code=data.get("zip_code"),
#             customer_id=current_user.id
#         )
#         db.session.add(new_address)
#         db.session.commit()
#         return jsonify({"message": "Address added successfully!"}), 201
    
