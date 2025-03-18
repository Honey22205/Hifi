    
import plotly.graph_objects as go
from markupsafe import Markup
import plotly.io as pio
from models import DeliveryAgent, Order
from sqlalchemy import func
from datetime import timedelta

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