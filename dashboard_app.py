import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import os

# Load student data
json_path = os.path.join(os.path.dirname(__file__), 'students_100.json')
df = pd.read_json(json_path)

app = dash.Dash(__name__)

# Pie chart for risk categories
risk_counts = df['Risk_Category'].value_counts()
pie_fig = px.pie(names=risk_counts.index, values=risk_counts.values, title='Dropout Risk Distribution')

# Scatter plot for grades vs absences colored by risk
scatter_fig = px.scatter(
    df,
    x='Aggregate_Grade',
    y='Number_of_Absences',
    color='Risk_Category',
    hover_data=['Name'],
    title='Grades vs Absences by Risk'
)

app.layout = html.Div([
    html.H1('Student Dropout Dashboard'),
    dcc.Graph(figure=pie_fig),
    dcc.Graph(figure=scatter_fig),
    html.Div('Interactive dashboard powered by Dash & Plotly.', style={'marginTop': 20})
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)
