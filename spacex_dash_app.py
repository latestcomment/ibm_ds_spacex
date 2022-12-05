# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Data prep

sites = ['ALL']
for site in (spacex_df['Launch Site'].unique()):
    sites.append(site)


success_rate_all = spacex_df.groupby(['Launch Site'])['class'].mean().reset_index(name='success_rate')

def compute_info(entered_site):
    df =  spacex_df[spacex_df['Launch Site']==str(entered_site)]

    success_rate_site = df.groupby(['class'])['class'].count().reset_index(name='cnt')
    for i in range(len(success_rate_site)):
        success_rate_site.loc[i,'perc'] = success_rate_site.loc[i,'cnt']/(sum(success_rate_site['cnt']))

    return success_rate_site

def filtered_df(entered_site):
    df =  spacex_df[spacex_df['Launch Site']==str(entered_site)]
    return df

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        
        # Heading
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={
                'textAlign': 'center',
                'color': '#503D36',
                'font-size': 40
            }
        ),

        # Dropdown Launch Sites
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {
                    'label':site,
                    'value':site
                }
                for site in sites
            ]
        ),
        html.Br(),

        # Pie chart
        html.Div(
            dcc.Graph(
                id='success-pie-chart'
            )
        ),
        html.Br(),

        # Slider
        html.Div(
            dcc.RangeSlider(
                id='payload-slider',
                min=0,
                max=10000,
                step=1000,
                marks={
                    0:'0',
                    100:'100'
                },
                value=[min_payload, max_payload]
            )
        ),
        html.Br(),

        # Scatter Chart
        html.Div(
            dcc.Graph(
                id='success-payload-scatter-chart'
            )
        ),
        html.Br()
    ]
)


# Callback decorator
@app.callback(
    Output(
            component_id='success-pie-chart',
            component_property='figure'
        ),
    Input(
        component_id='site-dropdown',
        component_property='value'
    )
)

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            success_rate_all,
            values='success_rate',
            names='Launch Site',
            title='Total Success Launches By Sites'
        )
        return fig
    else:
        
        fig = px.pie(
            compute_info(entered_site=entered_site),
            values='perc',
            names='class',
            title='Total Success Launches For Site {}'.format(entered_site)
        )
        return fig

@app.callback(
    Output(
        component_id='success-payload-scatter-chart',
        component_property='figure'
    ),
    [
        Input(
            component_id='site-dropdown',
            component_property='value'
        ),
        Input(
            component_id='payload-slider',
            component_property='value'
        ),
    ]
)

def get_scatter_chart(entered_site, slider):
    if entered_site == 'ALL':
        
        dff=spacex_df[(spacex_df['Payload Mass (kg)']>=slider[0])&(spacex_df['Payload Mass (kg)']<=slider[1])]

        fig_scatter = px.scatter(
            dff,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version'
        )
        return fig_scatter

    else:
        df = filtered_df(entered_site=entered_site)

        dff=df[(df['Payload Mass (kg)']>=slider[0])&(df['Payload Mass (kg)']<=slider[1])]

        fig_scatter = px.scatter(
            dff,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version'
        )
        return fig_scatter

if __name__ == '__main__':
    app.run_server()