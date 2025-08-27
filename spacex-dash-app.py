# Import required libraries
import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px

# Read the SpaceX data into pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Ensure consistent column name usage
spacex_df = spacex_df.rename(columns={'Payload Mass (kg)': 'PayloadMass'})

# Get min and max payload for slider
max_payload = spacex_df['PayloadMass'].max()
min_payload = spacex_df['PayloadMass'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        ],
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):", style={'font-size': 16}),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(min_payload): str(int(min_payload)),
               int(max_payload/4): str(int(max_payload/4)),
               int(max_payload/2): str(int(max_payload/2)),
               int(3*max_payload/4): str(int(3*max_payload/4)),
               int(max_payload): str(int(max_payload))},
        value=[min_payload, max_payload]
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(
            success_counts,
            values='count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        outcome_counts['class'] = outcome_counts['class'].map({1: 'Success', 0: 'Failed'})
        fig = px.pie(
            outcome_counts,
            values='count',
            names='class',
            title=f'Success vs. Failed Launches for {entered_site}'
        )
    return fig

# Callback for scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[(spacex_df['PayloadMass'] >= payload_range[0]) & 
                           (spacex_df['PayloadMass'] <= payload_range[1])]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='PayloadMass',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Launch Outcome for All Sites',
            labels={'PayloadMass': 'Payload Mass (kg)', 'class': 'Launch Outcome'}
        )
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='PayloadMass',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Launch Outcome for {entered_site}',
            labels={'PayloadMass': 'Payload Mass (kg)', 'class': 'Launch Outcome'}
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)