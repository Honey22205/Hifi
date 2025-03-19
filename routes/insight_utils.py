    
import plotly.graph_objects as go
from markupsafe import Markup
import plotly.io as pio
from models import DeliveryAgent, Order,DeliveryFeedback
from sqlalchemy import func
from datetime import timedelta
import matplotlib.pyplot as plt

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


# def generate_delivery_feedback_bar_chart():


    
#     agents = DeliveryFeedback.query.all()
#     ratings = []



#     fig = go.Figure()
#     fig.add_trace(go.Bar(y=suppliers, x=1, name="1", marker=dict(color='#1E3A8A'), orientation='h'))
#     fig.add_trace(go.Bar(y=suppliers, x=2, name="2", marker=dict(color='#6366F1'), orientation='h'))
#     fig.add_trace(go.Bar(y=suppliers, x=3, name="3", marker=dict(color='#FF8C00'), orientation='h'))
#     fig.add_trace(go.Bar(y=suppliers, x=4, name="4", marker=dict(color='#FF8C00'), orientation='h'))
#     fig.add_trace(go.Bar(y=suppliers, x=5, name="5", marker=dict(color='#FF8C00'), orientation='h'))


#     fig.update_layout(
#         title="📦 Delivery Performance by Delivery Agent (Real Data)",
#         xaxis=dict(title="Percentage"),
#         yaxis=dict(title="Delivery Agent", categoryorder="total ascending"),
#         barmode="stack",
#         template="plotly_white",
#         bargap=0.05,
#         height=400,
#     )

#     return Markup(fig.to_html(full_html=False))





def generate_agent_rating_chart():
    # Get all delivery agents
    agents = DeliveryAgent.query.all()

    agent_names = [agent.username for agent in agents]

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
        4: '#FFDE00',   # yellow
        5: '#0dec05',  # green
    }

    fig = go.Figure()

    # Add bars for each rating (grouped)
    for rating in range(1, 6):
        fig.add_trace(go.Bar(
            x=agent_names,
            y=[rating if ratings_count_per_agent[agent][rating] > 0 else 0 for agent in agent_names],  # bar height = rating
            name=f"{rating} Star",
            marker_color=colors[rating],
            text=[rating] * len(agent_names),
            textposition='inside'
        ))

    fig.update_layout(
        title="⭐ Delivery Agent Ratings (1 to 5 stars)",
        xaxis=dict(title="Delivery Agent"),
        # yaxis=dict(title="Number of Ratings"),
        yaxis=dict(title="Rating Scale (1 to 5)", tickmode='linear', dtick=1, range=[0.5, 5.5]),
        barmode='group',
        bargap=0.1,
        template="plotly_white",
        height=400
    )

    return Markup(fig.to_html(full_html=False))

