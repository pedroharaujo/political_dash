from src.app import app
import numpy as np
import pandas as pd
from pathlib import Path
# from src.TDQuery import TDQuery


data_ise = pd.read_excel('./data.xlsx', sheet_name='indicadores_socioeconomicos')
data_gastos = pd.read_excel('./data.xlsx', sheet_name='gastos_união_por_setor')

if __name__ == "__main__":
    # td_class = TDQuery()
    # schedule.every(12).hours.do(td_class.getAdUnitsList)
    # t = Thread(target=run_schedule)
    # t.start()
    app.run_server(debug=True, threaded=False)
