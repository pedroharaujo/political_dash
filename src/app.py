from dash import html, dcc
import dash_bootstrap_components as dbc
from .server import app, server
from . import callbacks
from .components import *

style_labels = {
    "font-weight": "bold",
    "text-align": "right",
    "font-size": 15,
    "offset": 1,
    "margin-right": "1em",
}


app.layout = html.Div(
    [
        header,
        html.Div(
            className="dropdownsDiv1",
            children=[
                dbc.Label("Date: ", style=style_labels, html_for="datePicker"),
                datepicker,
                button,
                checkbox,
            ],
            style={"display": "flex", "margin-top": "1em"},
        ),
        dcc.Loading(
            children=[
                html.Div(
                    className="graphs",
                    children=[
                        html.Div(
                            className="timeSeriesConversionDiv",
                            children=[dcc.Graph(id="timeSeriesConversion")],
                        )
                    ],
                ),
            ]
        ),
        dcc.Loading(
            children=[
                html.Div(
                    className="graphs",
                    children=[
                        html.Div(
                            className="DataTableDiv",
                            children=[datatable],
                        )
                    ],
                ),
            ]
        ),
    ],
)
