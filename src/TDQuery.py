import pandas as pd
import numpy as np
import plotly.express as px
import pytd
import pytd.pandas_td as td
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import seaborn as sns
import plotly.graph_objects as go


class TDQuery:
    def __init__(self) -> None:
        self.apikey = "10757/45b1cbf8c4df6e4ab2c770ed3cbaee2fb4ab8974"
        self.database = "etus_prod"
        self.engine = "presto"

    def td_query(self, query):
        client = pytd.Client(
            apikey=self.apikey, database=self.database, default_engine=self.engine
        )
        new_engine = td.create_engine(self.engine + ":etus_prod", con=client)
        data = td.read_td(query, new_engine)
        return data

    def queryData(self, start_date="2021-01-01", end_date="NULL"):
        payload = f"WITH A AS(\r\n  SELECT \r\n    DATE(FROM_UNIXTIME(time,\r\n        'America/Sao_Paulo')) AS DATE,\r\n    hashed_email,\r\n    td_host,\r\n    td_client_id,\r\n    utm_source,\r\n    td_path,\r\n    questions,\r\n    direct_to,\r\n    td_url,\r\n    CASE\r\n      WHEN (\r\n        direct_to LIKE '%/cartoes/%'\r\n        AND direct_to NOT LIKE '%/cartoes/s_/%'\r\n      ) THEN SPLIT(\r\n        direct_to,\r\n        '/'\r\n      ) [5]\r\n      WHEN (\r\n        direct_to LIKE '%/cartoes/%'\r\n        AND direct_to LIKE '%/cartoes/s_/%'\r\n      ) THEN SPLIT(\r\n        direct_to,\r\n        '/'\r\n      ) [7]\r\n      WHEN (\r\n        direct_to LIKE '%/recomendacao/%'\r\n      ) THEN SPLIT(\r\n        direct_to,\r\n        '/'\r\n      ) [7]\r\n      WHEN (\r\n        direct_to LIKE '%/r2/cc/%'\r\n      ) THEN SPLIT(\r\n        direct_to,\r\n        '/'\r\n      ) [7]\r\n      WHEN (\r\n        direct_to LIKE '%/r/cc/%'\r\n      ) THEN SPLIT(\r\n        direct_to,\r\n        '/'\r\n      ) [7]\r\n      ELSE NULL\r\n    END AS recomended_card\r\n  FROM\r\n    etus_prod.leads_recomendador\r\n  WHERE\r\n    TD_TIME_RANGE(time,\r\n      {start_date},\r\n      {end_date},\r\n      'America/Sao_Paulo')\r\n    AND td_host LIKE '%plusdin.com.br%'\r\n),\r\nB AS(\r\n  SELECT \r\n    time,\r\n    td_client_id,\r\n    td_os,\r\n    td_url,\r\n    td_browser,\r\n    td_screen,\r\n    td_viewport,\r\n    td_platform,\r\n    CASE\r\n      WHEN utm_source LIKE '%facebook%' THEN 'facebook'\r\n      WHEN utm_source LIKE '%google%' THEN 'google'\r\n      WHEN utm_source LIKE '%tiktok%' THEN 'tiktok'\r\n      ELSE 'direct'\r\n    END AS utm_source,\r\n    td_path,\r\n    CASE\r\n      WHEN td_path LIKE '%/cartoes/%'\r\n      AND td_path LIKE '%/porque-recomendamos%' THEN 'P1'\r\n      WHEN td_path LIKE '%/cartoes/%'\r\n      AND td_path LIKE '%/como-solicitar%' THEN 'P3'\r\n      ELSE NULL\r\n    END AS path_name,\r\n    CASE\r\n      WHEN (\r\n        td_path LIKE '%/cartoes/%'\r\n        AND td_path NOT LIKE '%/cartoes/s_/%'\r\n      ) THEN SPLIT(\r\n        td_path,\r\n        '/'\r\n      ) [3]\r\n      WHEN (\r\n        td_path LIKE '%/cartoes/%'\r\n        AND td_path LIKE '%/cartoes/s_/__/%'\r\n      ) THEN SPLIT(\r\n        td_path,\r\n        '/'\r\n      ) [5]\r\n      WHEN (\r\n        td_path LIKE '%/cartoes/%'\r\n        AND td_path LIKE '%/cartoes/s_/%'\r\n        AND td_path NOT LIKE '%/cartoes/s_/__/%'\r\n      ) THEN SPLIT(\r\n        td_path,\r\n        '/'\r\n      ) [4]\r\n      ELSE NULL\r\n    END AS recomended_card\r\n  FROM\r\n    etus_prod.pageviews\r\n  WHERE\r\n    TD_TIME_RANGE(time,\r\n      {start_date},\r\n      {end_date},\r\n      'America/Sao_Paulo')\r\n) SELECT \r\n  A.DATE,\r\n  A.td_client_id,\r\n  A.utm_source,\r\n  A.td_path,\r\n  B.path_name,\r\n  A.recomended_card\r\nFROM\r\n  A LEFT\r\nJOIN\r\n  B\r\n  ON A.recomended_card = B.recomended_card\r\n  AND A.td_client_id = B.td_client_id\r\nWHERE\r\n  B.path_name IS NOT NULL\r\nGROUP BY\r\n  A.DATE,\r\n  A.td_client_id,\r\n  A.utm_source,\r\n  A.td_path,\r\n  B.path_name,\r\n  A.recomended_card"
        self.data = self.td_query(query=payload)
        print("Data updated!")

    def processData(self):
        self.data = self.data.groupby(
            ["DATE", "td_client_id", "td_path", "recomended_card"], as_index=False
        ).agg({"path_name": set})
        self.data["converted"] = [
            1 if "P3" in case else 0 for case in self.data["path_name"]
        ]
        self.data.to_csv("./data.csv")
        self.data.to_json("./data.json")
        return self.data

    def getRecomendersConversionRate(self):
        df = (
            self.data.groupby(["DATE", "td_path"])["converted"].sum()
            / self.data.groupby(["DATE", "td_path"])["converted"].count()
        )
        df = df.reset_index()
        df["count"] = self.data.groupby(["DATE", "td_path"])["converted"].count().values
        self.data = df
        self.data.to_csv("./conversion_data.csv")
        self.data.to_json("./conversion_data.json")
        return self.data

    def getData(self):
        self.queryData()
        self.processData()
        return self.getRecomendersConversionRate()


if __name__ == "__main__":
    data = TDQuery().getData()
    data = pd.read_csv("./conversion_data.csv", index_col=0)
    print("DATA: ", data)
