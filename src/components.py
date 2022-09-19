# sourcery skip: use-datetime-now-not-today
import datetime
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from run import data, complete_data


header = html.Header(
    className="headName",
    children=[
        html.H2(
            "Plusdin Recommenders Evaluation Tool",
            style={
                "display": "inline-block",
                "font-size": 30,
                "color": "white",
                "margin-left": "1em",
            },
        ),
    ],
    style={
        "background-color": "darkblue",
        "height": "65px",
        "width": "100%",
    },
)

datepicker = dcc.DatePickerRange(
    id="datePicker",
    min_date_allowed=datetime.datetime(2021, 1, 1),
    max_date_allowed=datetime.datetime.today(),
    start_date=datetime.datetime(2021, 1, 1),
    end_date=datetime.datetime.today(),
    style={"margin-right": "1em"},
)

button = html.Button(
    "Submit",
    id="button",
    n_clicks=0,
    style={
        "height": "2.5em",
        "width": "6em",
        "color": "#fff",
        "background-color": "#007bff",
        "border-color": "#007bff",
        "border-radius": 3,
        "box-shadow": "0 0 0 0.1rem rgba(0, 123, 255, 0.5)",
    },
)

checkbox = dcc.Checklist(
    id="checkbox", options=[{"label": "Group table by date", "value": "yes"}]
)

datatable = dash_table.DataTable(
    id="datatable",
    sort_action="native",
    filter_action="native",
    style_data={
        "whiteSpace": "normal",
        "height": "auto",
    },
    style_table={
        "overflowX": "auto",
        "minWidth": "100%",
        "height": "300px",
        "overflowY": "auto",
    },
    style_cell={
        "height": "auto",
        "minWidth": "180px",
        "width": "180px",
        "maxWidth": "180px",
        "whiteSpace": "normal",
    },
)
