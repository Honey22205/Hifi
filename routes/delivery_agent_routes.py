import datetime
import os
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from models import Address, Customer, DeliveryAgent, DeliveryFeedback, Earnings, Order, OrderItem


def delivery_agent_routes(app, db):
    @app.route('/delivery-agent')
    def delivery_agent():
        # Get the delivery agent using the current user's ID
        print(current_user)
        agent = DeliveryAgent.query.get(current_user.id)
        print(agent)
        
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
                Order.status == "Delivered"  or Order.status == "Pending" or Order.status == "Accepted"
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
        
        # Query to get today's earnings (sum of each field)
        today_earnings = db.session.query(
            func.coalesce(func.sum(Earnings.base_pay), 0).label("base_pay"),
            func.coalesce(func.sum(Earnings.bonus), 0).label("bonus"),
            func.coalesce(func.sum(Earnings.trips_count), 0).label("trips"),
            # func.count(Earnings.id).label("delivery_count")
        ).filter(
            Earnings.delivery_agent_id == current_user.id,
            func.date(Earnings.earned_at) == datetime.date.today()
        ).first()

        # Query to get the most recent earnings record
        recent_earning = Earnings.query.filter(
            Earnings.delivery_agent_id == current_user.id
        ).order_by(Earnings.earned_at.desc()).first()
        
        
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
            timedelta=datetime.timedelta,
            earnings=today_earnings,
            recent_earnings=recent_earning
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
        """Fetch detailed order information along with order items, customer details, and feedback."""
        
        order = (
            db.session.query(Order)
            .options(
                joinedload(Order.user).joinedload(Customer.addresses),  # Load customer's addresses
                joinedload(Order.items).joinedload(OrderItem.menu_item)   # Load each order item's menu details
            )
            .filter(
                Order.delivery_agent_id == current_user.id,
                Order.id == order_id
            )
            .first()
        )
        
        if not order:
            return "Order not found", 404

        # Fetch the delivery feedback associated with the current order and delivery agent
        feedback = (
            db.session.query(DeliveryFeedback)
            .filter(
                DeliveryFeedback.delivery_agent_id == current_user.id,
                DeliveryFeedback.order_id == order_id
            )
            .first()
        )
        
        print(feedback)
        
        return render_template("delivery_agent/order_detail.html", user=current_user, order=order, feedback=feedback)
    
    @app.route('/delivery-partner/order-tracking/<int:order_id>')
    def delivery_partner_order_tracking(order_id):
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
        
        return render_template("delivery_agent/track_order.html", user=current_user, order=order)



    @app.route('/order/<int:order_id>/accept', methods=['POST'])
    @login_required
    def accept_order(order_id):
        order = Order.query.get_or_404(order_id)
        
        # Ensure order is pending and not already assigned
        if order.status != "Pending":
            flash("Order Already accepted.")
            return redirect(url_for("delivery_agent"))
        
        order.status = "Accepted"
        order.delivery_status = "Accepted"
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

#  Update request for Delivery_Status
    @app.route('/api/orders/<int:order_id>/update_status', methods=['POST'])
    def edit_delivery_status(order_id):
        order = Order.query.get_or_404(order_id)
        
        valid_statuses = ["Accepted", "Picked Up", "Out for Delivery", "Delivered"]
        data = request.get_json() or {}
        new_status = data.get('status')
        
        if new_status not in valid_statuses:
            return jsonify({"error": "Invalid status update"}), 400

        order.delivery_status = new_status
        if new_status == "Delivered":
            order.status = "Delivered"
            order.delivered_at = func.now()
            
            # Define the base pay per delivery.
            base_pay_per_delivery = 50.0
            
            # Determine today's date.
            today = func.date(func.now())
            
            # Query today's earnings record for the current delivery agent.
            today_earnings = Earnings.query.filter(
                Earnings.delivery_agent_id == current_user.id,
                func.date(Earnings.earned_at) == today
            ).first()
            
            if today_earnings:
                # Update today's earnings.
                today_earnings.base_pay += base_pay_per_delivery
                today_earnings.trips_count += 1
                # Add bonus for every 5 trips.
                if today_earnings.trips_count % 5 == 0:
                    today_earnings.bonus += 100.0
            else:
                # Retrieve the most recent earnings record before today to carry forward totals.
                previous_earnings = Earnings.query.filter(
                    Earnings.delivery_agent_id == current_user.id,
                    func.date(Earnings.earned_at) < today
                ).order_by(Earnings.earned_at.desc()).first()
                
                initial_base_pay = previous_earnings.base_pay if previous_earnings else 0.0
                initial_bonus = previous_earnings.bonus if previous_earnings else 0.0
                
                # Create a new earnings record for today.
                today_earnings = Earnings(
                    delivery_agent_id=current_user.id,
                    base_pay=initial_base_pay + base_pay_per_delivery,
                    bonus=initial_bonus,
                    trips_count=1,
                    earned_at=func.now()
                )
                db.session.add(today_earnings)

        db.session.commit()
        
        # Build response data including earnings details for a delivered order.
        response_data = {
            "order_id": order.id,
            "delivery_status": order.delivery_status
        }
        if new_status == "Delivered" and order.delivery_agent_id:
            earnings = Earnings.query.filter_by(delivery_agent_id=order.delivery_agent_id).first()
            if earnings:
                total = earnings.base_pay + earnings.bonus
                response_data["earnings"] = {
                    "base_pay": earnings.base_pay,
                    "bonus": earnings.bonus,
                    "trips_count": earnings.trips_count,
                    "total": total
                }
            
        return jsonify(response_data), 200





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
    
    
    
    # @app.route('/api/orders/<int:order_id>/update_status', methods=['POST'])
    # @login_required
    # def update_order_status(order_id):
    #     order = Order.query.get_or_404(order_id)
        
    #     # Define the sequence of statuses
    #     status_sequence = ["Accepted", "Picked Up", "Out for Delivery", "Completed"]

    #     # Ensure the current delivery_status is one of the expected values
    #     if order.delivery_status not in status_sequence:
    #         return jsonify({'error': 'Invalid delivery status'}), 400

    #     # If the order is already completed, no update is necessary
    #     if order.delivery_status == "Completed":
    #         return jsonify({'message': 'Order is already completed'}), 400

    #     # Find the current index and move to the next status in the sequence
    #     current_index = status_sequence.index(order.delivery_status)
    #     next_index = current_index + 1
    #     order.delivery_status = status_sequence[next_index]

    #     # When status reaches "Completed", update the main status, delivered_at, and earnings
    #     if order.delivery_status == "Completed":
    #         order.status = "Completed"
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

    #     db.session.commit()

    #     response = {
    #         'message': 'Order delivery status updated successfully',
    #         'delivery_status': order.delivery_status
    #     }
        
    #     if order.delivery_status == "Completed":
    #         response['earnings'] = {
    #             'base_pay': today_earnings.base_pay,
    #             'bonus': today_earnings.bonus,
    #             'trips_count': today_earnings.trips_count,
    #             'total': today_earnings.base_pay + today_earnings.bonus
    #         }
        
    #     return jsonify(response)


    @app.route('/api/delivery-agent/earnings')
    @login_required
    def get_current_earnings():
        today_earnings = Earnings.query.filter(
            Earnings.delivery_agent_id == current_user.id,
            func.date(Earnings.earned_at) == func.date(func.now())
        ).first()

        if not today_earnings:
            return jsonify({
                'base_pay': 0.0,
                'bonus': 0.0,
                'trips_count': 0
            })

        return jsonify({
            'base_pay': today_earnings.base_pay,
            'bonus': today_earnings.bonus,
            'trips_count': today_earnings.trips_count
        })
    
    # @app.route('/delivery-agent/earnings/<int:agent_id>')
    # @login_required
    # def get_agent_earnings(agent_id):
    #     # Query earnings for the specific delivery agent
    #     earnings = Earnings.query.filter_by(delivery_agent_id=agent_id).all()
        
    #     # Format the earnings data
    #     earnings_data = [{
    #         'base_pay': earning.base_pay,
    #         'bonus': earning.bonus,
    #         'trips_count': earning.trips_count,
    #         'earned_at': earning.earned_at.strftime('%Y-%m-%d %H:%M:%S'),
    #         'total': earning.base_pay + earning.bonus
    #     } for earning in earnings]
        
    #     return jsonify(earnings_data)
