from dash import Dash, dcc, html
import plotly.express as px

app = Dash(__name__)

def display_alt(data_f, args, kwargs):
    data = data_f(*args, **kwargs)
    fig = px.scatter(data, x='ts', y='alt', color='spd')

    return fig

def display_spd(data_f, args, kwargs):
    data = data_f(*args, **kwargs)
    fig = px.scatter(data, x='ts', y='spd', color='alt')
    #fig.update_traces(line_smoothing=0.4)

    return fig

def display_map(data_f, args, kwargs):
    data = data_f(*args, **kwargs)
    fig = px.scatter_mapbox(data, lat='lat', lon='lon', color='spd', mapbox_style='stamen-terrain', width=1400, height=800)
    #fig.update_traces(mode='lines', marker_size=2, line_shape='spline')

    return fig

def run_dashboard(data_f, *args, **kwargs):
    app.layout = html.Div([
        html.H4('Ski Plot'),
        dcc.Graph(id='map', figure=display_map(data_f, args, kwargs)),
        html.H4('Altitude'),
        dcc.Graph(id='alt_plot', figure=display_alt(data_f, args, kwargs)),
        html.H4('Speed'),
        dcc.Graph(id='spd_plot', figure=display_spd(data_f, args, kwargs))
    ])

    app.run_server(debug=True)
