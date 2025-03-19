import base64
import datetime
import io
from flask import flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required
from matplotlib import pyplot as plt
import pandas as pd
from sqlalchemy import desc, func
import seaborn as sns
import matplotlib.dates as mdates
import plotly.express as px
from datetime import datetime, timedelta, timezone

from models import Customer, DeliveryAgent, Order
from routes.insight_utils import calculate_average_delivery_time, calculate_delivery_partner_performance, calculate_on_time_order_percentage, calculate_return_refund_statistics, calculate_revenue_per_delivery, generate_agent_rating_chart, generate_line_chart, generate_monthly_retention_chart, generate_pie_chart,generate_bar_chart


def admin_routes(app, db):
    @app.route('/admin')
    def admin():
        if not current_user.is_authenticated:
            return redirect(url_for('employee_login'))
        
        # Aggregated order data by date for sales chart
        orders = db.session.query(
            func.date(Order.created_at).label("order_date"),
            func.sum(Order.total_price).label("total_sales")
        ).group_by(func.date(Order.created_at))\
        .order_by(func.date(Order.created_at))\
        .all()
        
        # Total orders count
        total_orders = db.session.query(func.count(Order.id)).scalar()
        
        # Total users count (assuming customers represent users)
        total_users = db.session.query(func.count(Customer.id)).scalar()
        
        # Overall total sales from all orders
        overall_total_sales = db.session.query(func.coalesce(func.sum(Order.total_price), 0)).scalar()
        
        # New users: customers created in the last 30 days. 
        # If your Customer model does not yet include a created_at column, add one or adjust this logic.
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        delivery_partners = db.session.query(func.count(DeliveryAgent.id)).scalar()
        # if hasattr(Customer, 'created_at'):
        #     new_users = db.session.query(func.count(Customer.id))\
        #                 .filter(Customer.created_at >= thirty_days_ago)\
        #                 .scalar()
        
        # Query recent orders (limit to last 10 orders)
        recent_orders = Order.query.order_by(desc(Order.created_at)).limit(10).all()

        # Prepare sales chart
        if orders:
            # Convert query result to DataFrame
            df = pd.DataFrame(orders, columns=['order_date', 'total_sales'])
            df['order_date'] = pd.to_datetime(df['order_date'])
            
            # Create Plotly line chart with markers
            fig = px.line(df, x='order_date', y='total_sales', markers=True,
                        title="📊 Order Trend Over Time",
                        labels={'order_date': 'Date', 'total_sales': 'Total Sales (₹)'})
            fig.update_layout(
                hovermode="x unified",
                template="plotly_white",
                height=400,
                xaxis=dict(
                    rangeselector=dict(
                        buttons=[
                            dict(count=7, label="1w", step="day", stepmode="backward"),
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(step="all")
                        ]
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                )
            )
            chart_html = fig.to_html(full_html=False)
            message = ""
        else:
            chart_html = None
            message = "No sales data available."

        return render_template('admin/home.html',
                            chart_html=chart_html,
                            message=message,
                            total_orders=total_orders,
                            total_users=total_users,
                            overall_total_sales=overall_total_sales,
                            delivery_partners=delivery_partners,
                            recent_orders=recent_orders)

    
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
    
    @app.route('/admin/insights')
    @login_required
    def insights():
        if not current_user.is_authenticated:
            return redirect(url_for('employee_login'))
        
        # Fetching charts (demo and database reflected)

        charts = []

        chart_html = generate_pie_chart()           # Demo data chart
        bar_chart = generate_bar_chart()              # Demo data chart
        line_chart_html = generate_line_chart()       # Data from the database
        delivery_rating_bar = generate_agent_rating_chart()
        monthly_retention_chart=generate_monthly_retention_chart()

        charts.append(chart_html)
        charts.append(bar_chart)
        charts.append(line_chart_html)
        charts.append(delivery_rating_bar)
        charts.append(monthly_retention_chart)



        
        # Compute analysis statistics with optimized queries:
        avg_delivery_time = calculate_average_delivery_time() 
        delivery_partner_performance = calculate_delivery_partner_performance()
        return_refund_percentage = calculate_return_refund_statistics()
        on_time_order_percentage = calculate_on_time_order_percentage()
        revenue_per_delivery = calculate_revenue_per_delivery()
        
        return render_template(
            'admin/insights.html',
            charts=charts,

            avg_delivery_time=avg_delivery_time,
            delivery_partner_performance=delivery_partner_performance,
            return_refund_percentage=return_refund_percentage,
            on_time_order_percentage=on_time_order_percentage,
            revenue_per_delivery=revenue_per_delivery
        )