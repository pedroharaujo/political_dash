import dash
from flask import Flask


server = Flask("src")
app = dash.Dash(server=server)
