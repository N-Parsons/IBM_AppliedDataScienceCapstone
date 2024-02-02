# Import required libraries
import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Filtered by launch site
spacex_df_site = spacex_df


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id = "site-dropdown",
                                    options = [
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                    ],
                                    value = "ALL",
                                    placeholder = "Select a Launch Site",
                                    searchable = True,
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(
                                    id = 'success-pie-chart',
                                )),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id = "payload-slider",
                                    min = min_payload,
                                    max = max_payload,
                                    value = [min_payload, max_payload],
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def update_success_pie_chart(selected):
    if selected == "ALL":
        pie_data = spacex_df[spacex_df["class"] == 1]["Launch Site"].value_counts().reset_index()
        pie_params = {
            "values": "count",
            "names": "Launch Site",
            "title": "Total Successful Launches by Launch Site",
            "category_orders": {
                "Launch Site": [*np.sort(spacex_df["Launch Site"].unique())]
            },
        }
    else:
        filtered_data = spacex_df[spacex_df["Launch Site"] == selected]

        pie_data = filtered_data["class"].value_counts().reset_index()
        pie_data["Outcome"] = pie_data["class"].map(map_success)

        pie_params = {
            "values": "count",
            "names": "Outcome",
            "color": "Outcome",
            "color_discrete_map": {"Success": "green", "Failure": "tomato"},
            "category_orders": {"Outcome": ["Success", "Failure"]},
            "title": f"Success/Failure for Launch Site: {selected}",
        }

    return px.pie(
        pie_data,
        **pie_params,
    )


def map_success(value):
    return "Success" if value else "Failure"

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def update_payload_scatter_chart(selected, payload):
    if selected == "ALL":
        data = spacex_df
    else:
        data = spacex_df[spacex_df["Launch Site"] == selected]

    data = data[data["Payload Mass (kg)"] <= payload[1]].reset_index()[data["Payload Mass (kg)"] >= payload[0]].reset_index()

    data["Outcome"] = data["class"].map(map_success)
    
    fig = px.scatter(
        data,
        x = "Payload Mass (kg)",
        y = "Outcome",
        color = "Booster Version Category",
        #symbol = "Booster Version Category",
    )

    fig.update_traces(marker = {"size": 15})

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
