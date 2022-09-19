import json
from fileinput import filename
from tabnanny import check
import pandas as pd
import numpy as np
import plotly.express as px
from .server import app
from dash.dependencies import Input, Output, State
from run import data, complete_data

# ## TAB 1 CALLBACKS
@app.callback(
    [Output("timeSeriesConversion", "figure")],
    [Input("button", "n_clicks"), Input("checkbox", "value")],
    [State("datePicker", "start_date"), State("datePicker", "end_date")],
)
def updatePlot(click, checkbox, start_date, end_date):
    if not (click is not None) & (click >= 1):
        return [{}]
    if "T" in start_date:
        start_date = str(start_date).split("T")[0]
    if "T" in end_date:
        end_date = str(end_date).split("T")[0]

    df = data[(data["DATE"] >= start_date) & (data["DATE"] <= end_date)]

    fig = px.line(
        df,
        x="DATE",
        y="converted",
        color="td_path",
        hover_data=["DATE", "td_path", "count"],
        title="Recommenders Conversion Through Time",
    )
    return [fig]


@app.callback(
    [Output("datatable", "data"), Output("datatable", "columns")],
    [Input("button", "n_clicks"), Input("checkbox", "value")],
    [State("datePicker", "start_date"), State("datePicker", "end_date")],
)
def updateTable(click, checkbox, start_date, end_date):
    if not (click is not None) & (click >= 1):
        return [None, []]
    if "T" in start_date:
        start_date = str(start_date).split("T")[0]
    if "T" in end_date:
        end_date = str(end_date).split("T")[0]

    df_complete = complete_data[
        (complete_data["DATE"] >= start_date) & (complete_data["DATE"] <= end_date)
    ]
    if checkbox == ["yes"]:
        columns_to_group = ["td_path", "recomended_card"]
    else:
        columns_to_group = ["DATE", "td_path", "recomended_card"]

    final_datatable = df_complete.groupby(columns_to_group, as_index=False)[
        "converted"
    ].sum()
    final_datatable["count"] = (
        df_complete.groupby(columns_to_group)["converted"].count().values
    )
    final_datatable["conversionRate"] = (
        final_datatable["converted"] / final_datatable["count"]
    )
    final_datatable["conversionRate"] = (
        final_datatable["converted"] / final_datatable["count"]
    )
    return [
        final_datatable.to_dict("records"),
        [
            {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in final_datatable.columns
        ],
    ]
