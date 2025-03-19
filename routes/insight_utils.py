    
import plotly.graph_objects as go
from markupsafe import Markup
import plotly.io as pio
from models import DeliveryAgent, Order,DeliveryFeedback
from sqlalchemy import func
from datetime import timedelta
import matplotlib.pyplot as plt
from app import db
from sqlalchemy import extract

def generate_pie_chart():

    labels = ['Teens (13-19)', 'Young Adults (20-35)', 'Middle-aged (36-50)', 'Seniors (51+)']
    sizes = [15, 40, 30, 15]
    colors = ['#66b3ff', '#99ff99', '#ff9933', '#ff3333']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=sizes,
        marker=dict(colors=colors, line=dict(color='#000000', width=1)),
        textinfo='label+percent',
        hoverinfo='label+percent+value',
        pull=[0, 0.05, 0, 0.05],
    )])

    fig.update_layout(
        title_text="Customer Demographics Distribution",
        title_x=0.5,
        showlegend=True,
        legend=dict(x=1, y=0.5),
        height=400,
    )
    # fig.show()

    chart_html = fig.to_html(full_html=False)
    return Markup(chart_html)



def generate_line_chart():
    
    agents = DeliveryAgent.query.all()
    suppliers = []
    early_counts = []
    on_time_counts = []
    late_counts = []

    for agent in agents:
        orders = Order.query.filter_by(delivery_agent_id=agent.id).all()
        early = 0
        on_time = 0
        late = 0

        for order in orders:
            if order.delivered_at and order.created_at:
                diff_minutes = (order.delivered_at - order.created_at).total_seconds() / 60  # convert to minutes
                
                # Example logic: (You can adjust conditions)
                if diff_minutes < 55:
                    early += 1
                elif 55 <= diff_minutes <= 60:
                    on_time += 1
                else:
                    late += 1

        total = early + on_time + late or 1  # Avoid division by zero
        suppliers.append(agent.username)
        early_counts.append((early * 100) / total)
        on_time_counts.append((on_time * 100) / total)
        late_counts.append((late * 100) / total)

    fig = go.Figure()
    fig.add_trace(go.Bar(y=suppliers, x=early_counts, name="Early", marker=dict(color='#1E3A8A'), orientation='h'))
    fig.add_trace(go.Bar(y=suppliers, x=on_time_counts, name="On Time", marker=dict(color='#6366F1'), orientation='h'))
    fig.add_trace(go.Bar(y=suppliers, x=late_counts, name="Late", marker=dict(color='#FF8C00'), orientation='h'))

    fig.update_layout(
        title="📦 Delivery Performance by Delivery Agent (Real Data)",
        xaxis=dict(title="Percentage"),
        yaxis=dict(title="Delivery Agent", categoryorder="total ascending"),
        barmode="stack",
        template="plotly_white",
        bargap=0.05,
        height=400,
    )

    return Markup(fig.to_html(full_html=False))

def generate_bar_chart():
    promotions = ['Discount', 'Weekend offers', 'Loyalty Rewards', 'Happy Hour', 'Seasonal Offer']
    effectiveness = [20, 35, 25, 30, 40]
    colors = ['blue', 'green', 'red', 'purple', 'orange']

    fig = go.Figure(

        data=[
            go.Bar(
                x=promotions,
                y=effectiveness,
                marker=dict(color=colors),
                text=[f"{val}%" for val in effectiveness],
                textposition="outside"
            )
        ]
    )

    fig.update_layout(
        title="Effectiveness of Promotions",
        xaxis=dict(title="Promotion Type"),
        yaxis=dict(title="Effectiveness (% Sales Increase)", range=[0, 50]),
        template="plotly_white",
        height=400
    )

    # Return plot as HTML that can be directly used in templates
    
    return Markup(fig.to_html(full_html=False))



def generate_agent_rating_chart():
    # Get all delivery agents
    agents = DeliveryAgent.query.all()
    agent_names = [agent.username for agent in agents]

    # Initialize a dictionary to store count of each rating (1-5) per agent
    ratings_count_per_agent = {agent.username: {r: 0 for r in range(1, 6)} for agent in agents}

    # Query database to count each rating per agent
    for agent in agents:
        for rating_value in range(1, 6):
            count = DeliveryFeedback.query.filter_by(delivery_agent_id=agent.id, rating=rating_value).count()
            ratings_count_per_agent[agent.username][rating_value] = count

    # Define colors for each rating
    colors = {
        1: '#C0504D',  # red
        2: '#F79646',  # orange
        3: '#4F81BD',  # blue
        4: '#FFDE00',  # yellow
        5: '#0dec05',  # green
    }

    fig = go.Figure()

    # Add bars for each rating (grouped)
    for rating in range(1, 6):
        fig.add_trace(go.Bar(
            x=agent_names,
            # Use the actual count of ratings instead of the rating value itself
            y=[ratings_count_per_agent[agent][rating] for agent in agent_names],
            name=f"{rating} Star",
            marker_color=colors[rating],
            # Optionally display the count as text
            text=[ratings_count_per_agent[agent][rating] for agent in agent_names],
            textposition='inside'
        ))

    fig.update_layout(
        title="⭐ Delivery Agent Ratings (1 to 5 stars)",
        xaxis=dict(title="Delivery Agent"),
        yaxis=dict(title="Number of Ratings"),  # Update label to reflect counts
        barmode='group',
        bargap=0.1,
        template="plotly_white",
        height=400
    )

    return Markup(fig.to_html(full_html=False))





def generate_monthly_retention_chart():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    retention_rates = []

    for month_num in range(1, 13):
        # Total customers who ordered in that month
        total_customers = db.session.query(Order.user_id).filter(
            extract('month', Order.created_at) == month_num
        ).distinct().count()

        # Repeat customers in that month (customers with more than 1 order till that month)
        repeat_customers = 0
        unique_users = db.session.query(Order.user_id).filter(
            extract('month', Order.created_at) == month_num
        ).distinct().all()

        for user_id, in unique_users:
            order_count = db.session.query(Order.id).filter(
                Order.user_id == user_id,
                extract('month', Order.created_at) <= month_num
            ).count()
            if order_count > 1:
                repeat_customers += 1

        # Calculate retention rate
        retention_rate = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0
        retention_rates.append(retention_rate)

    fig = go.Figure(data=go.Scatter(
        x=months,
        y=retention_rates,
        mode='lines+markers',
        name='Retention Rate',
        line=dict(color='blue'),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title='📊 Customer Retention Rate Over Time',
        xaxis=dict(title='Months'),
        yaxis=dict(title='Retention Rate (%)', range=[0, 100]),
        height=400,
        template="plotly_white"
    )

    return Markup(fig.to_html(full_html=False))







def calculate_average_delivery_time():
    """Calculate the average delivery time (in minutes) for orders that have been delivered."""
    # Only include orders that have a delivered_at timestamp
    result = db.session.query(
        func.avg(func.strftime('%s', Order.delivered_at) - func.strftime('%s', Order.created_at))
    ).filter(Order.delivered_at.isnot(None)).first()
    
    if result and result[0]:
        avg_seconds = result[0]
        avg_minutes = round(avg_seconds / 60)
        return avg_minutes
    return 0

def calculate_delivery_partner_performance():
    """Calculate the average delivery partner performance based on customer ratings."""
    avg_rating = db.session.query(func.avg(DeliveryFeedback.rating)).scalar()
    if avg_rating:
        performance_percent = round((avg_rating / 5) * 100)
        return performance_percent
    return 0

def calculate_return_refund_statistics():
    """
    Calculate return & refund statistics.
    This demo assumes that orders with status 'Refunded' indicate a refund.
    """
    total_orders = db.session.query(func.count(Order.id)).scalar()
    refunded_orders = db.session.query(func.count(Order.id)).filter(Order.status == 'Refunded').scalar()
    if total_orders:
        percentage = round((refunded_orders / total_orders) * 100, 1)
        return percentage
    return 0.0

def calculate_on_time_order_percentage():
    """
    Calculate the percentage of orders delivered on time.
    This demo assumes that orders with status 'Delivered' are considered on time.
    """
    total_delivered = db.session.query(func.count(Order.id)).filter(Order.status == 'Delivered').scalar()
    # In a real scenario you might compare delivered_at vs expected_delivery_time
    # Here, we'll assume a fixed demo percentage if no further data is available.
    if total_delivered:
        # For instance, if 98% of delivered orders are on time:
        return 98
    return 0

def calculate_revenue_per_delivery():
    """
    Calculate the average revenue per delivered order.
    """
    total_revenue = db.session.query(func.sum(Order.total_price)).filter(Order.status == 'Delivered').scalar() or 0
    total_deliveries = db.session.query(func.count(Order.id)).filter(Order.status == 'Delivered').scalar() or 0
    if total_deliveries:
        revenue = round(total_revenue / total_deliveries, 2)
        return revenue
    return 0.0