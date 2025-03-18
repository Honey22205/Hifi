import base64
import io
from flask import flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required
from matplotlib import pyplot as plt
import pandas as pd
from sqlalchemy import func
import seaborn as sns
import matplotlib.dates as mdates
import plotly.express as px

from models import DeliveryAgent, Order


def admin_routes(app, db):
    @app.route('/admin')
    def admin():
        if not current_user.is_authenticated:
            return redirect(url_for('employee_login'))
        
        # Fetch aggregated order data by date using SQLAlchemy ORM.
        orders = db.session.query(
            func.date(Order.created_at).label("order_date"),
            func.sum(Order.total_price).label("total_sales")
        ).group_by(func.date(Order.created_at))\
        .order_by(func.date(Order.created_at))\
        .all()

        if not orders:
            return render_template('admin/home.html', chart_html=None, message="No sales data available.")

        # Convert the query result to a Pandas DataFrame.
        df = pd.DataFrame(orders, columns=['order_date', 'total_sales'])
        df['order_date'] = pd.to_datetime(df['order_date'])

        # Create an interactive Plotly line chart with markers.
        fig = px.line(df, x='order_date', y='total_sales', markers=True,
                    title="📊 Order Trend Over Time",
                    labels={'order_date': 'Date', 'total_sales': 'Total Order (₹)'})

        # Enhance interactivity: add a range slider and selection buttons.
        fig.update_layout(
            hovermode="x unified",
            template="plotly_white",
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

        # Convert the Plotly figure to HTML (without full HTML headers) to embed in the template.
        chart_html = fig.to_html(full_html=False)

        return render_template('admin/home.html', chart_html=chart_html)

    
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
        # Fetch aggregated order data by date using SQLAlchemy ORM.
        orders = db.session.query(
            func.date(Order.created_at).label("order_date"),
            func.sum(Order.total_price).label("total_sales")
        ).group_by(func.date(Order.created_at))\
        .order_by(func.date(Order.created_at))\
        .all()

        if not orders:
            return render_template('admin/home.html', image_url=None, message="No sales data available.")

        # Convert query result to a DataFrame
        df = pd.DataFrame(orders, columns=['order_date', 'total_sales'])
        
        # Convert order_date to datetime
        df['order_date'] = pd.to_datetime(df['order_date'])

        # Set plot style and create the figure
        sns.set_style("whitegrid")
        plt.figure(figsize=(14, 6))

        # Create the line plot
        sns.lineplot(x=df['order_date'], y=df['total_sales'], marker='o', color='b',
                    linewidth=2.5, label="Total Order")

        # Format the x-axis for dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df) // 10)))
        plt.xticks(rotation=45, ha="right")

        # Add data labels at intervals
        for i in range(0, len(df), max(1, len(df) // 8)):
            plt.text(df['order_date'][i], df['total_sales'][i] + 5,
                    f"{int(df['total_sales'][i])}",
                    fontsize=10, ha='center', color='black', fontweight='bold')

        # Set labels and title
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Total Order (₹)", fontsize=12)
        plt.title("📊 Order Trend Over Time", fontsize=14, fontweight="bold")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)

        # Save the plot to an in-memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)

        # Encode the image as base64 and create a data URL
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        image_url = f"data:image/png;base64,{image_base64}"

        return render_template('admin/insights.html', image_url=image_url)
