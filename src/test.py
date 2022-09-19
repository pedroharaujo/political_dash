import pandas as pd


data = pd.read_csv("./data.csv", index_col=0)

data = (
    data.groupby(["DATE", "td_path"])["converted"].sum()
    / data.groupby(["DATE", "td_path"])["converted"].count()
)

data = data.reset_index()

print("DATA: ", data)
