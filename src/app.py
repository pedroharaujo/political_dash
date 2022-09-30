import dash
from flask import Flask
import dash_bootstrap_components as dbc
from dash import html, dcc
from . import callbacks
from .components import *
from dash import Input, Output, dcc, html


style_labels = {
    "font-weight": "bold",
    "text-align": "right",
    "font-size": 15,
    "offset": 1,
    "margin-right": "1em",
}


server = Flask("Political Dash")

app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return home
    elif pathname == "/page-1":
        return indicadores_socioeconomicos
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )
