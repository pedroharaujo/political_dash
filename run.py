from src.app import app
import numpy as np
import pandas as pd
from pathlib import Path
from src.TDQuery import TDQuery
from src.auxFunctions import *


data = pd.read_csv("./conversion_data.csv", index_col=0)
complete_data = pd.read_csv("./data.csv", index_col=0)

if __name__ == "__main__":
    # td_class = TDQuery()
    # schedule.every(12).hours.do(td_class.getAdUnitsList)
    # t = Thread(target=run_schedule)
    # t.start()
    app.run_server(debug=True, threaded=False)
