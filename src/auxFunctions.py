import json
import re
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
import datetime
import xgboost

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error as mse

from forex_python.converter import get_rate


def processData(data):
    # data = data.iloc[:2500000, :]

    print("Processing Data...")
    data["sold"] = data["sold"].astype(str).str.lower()
    data = data[~data["brius_cpm"].isna()]
    data["brius_cpm"] = data["brius_cpm"].astype(float)
    data["priceRule"] = data["priceRule"].astype(float)
    data["weekDay"] = [
        datetime.datetime.strptime(case, "%Y-%m-%d").strftime("%A")
        for case in data["DATE"]
    ]
    remove_slots = [
        "Ancora",
        "Ancora_Mobile",
        "Ancor_Desktop",
        "CozinhAZ",
        "FooterArtigo",
        "Footer_2",
        "HF_mobile_top",
        "HeaderDesktopHome",
        "InRead00_Mobile",
        "InRead01",
        "InRead02",
        "InRead03",
        "InRead04",
        "InRead06",
        "InRead3006002",
        "InRead320100",
        "InRead5",
        "Sidebar250",
        "Sidebar300250",
        "Sidebar300600",
        "clone",
        "ranking",
        "testing",
    ]

    data = data[~data["slot_id"].isin(remove_slots)].reset_index(drop=True)

    data["cpm"] = np.where(
        data["brius_cpm"].astype(float) >= data["priceRule"],
        data["brius_cpm"],
        data["priceRule"],
    )

    gc = ["DATE", "weekDay", "slot_id", "src", "td_path"]

    tmp = data.groupby(gc, as_index=False).agg({"sold": set})

    new_cases = []
    for i in tqdm(range(tmp.shape[0])):
        case = tmp.loc[i, "sold"]
        if len(case) == 1:
            if "false" in case:
                new_case = tmp.loc[i, :].copy()
                new_case["sold"] = "true"
            else:
                new_case = tmp.loc[i, :].copy()
                new_case["sold"] = "false"
            new_cases.append(new_case)

    new_cases_df = pd.DataFrame(new_cases)
    new_cases_df["cont"] = 0

    wm = lambda x: np.average(x, weights=data.loc[x.index, "cont"])

    grouped_data = data.groupby(gc + ["sold"], as_index=False).agg(
        {
            "cont": "sum",
            "brius_cpm": "mean",
            "priceRule": "mean",
            "cpm": "mean",
        }
    )

    grouped_data = pd.concat([grouped_data, new_cases_df])

    grouped_data["coverage"] = grouped_data["cont"] / grouped_data.groupby(gc)[
        "cont"
    ].transform("sum")

    grouped_data = grouped_data[
        (grouped_data["coverage"] != 0) & (grouped_data["coverage"] != 1)
    ]

    grouped_data = grouped_data[grouped_data["sold"] == "true"].reset_index(drop=True)

    grouped_data["EstimatedRevenue"] = grouped_data["coverage"] * grouped_data["cpm"]

    grouped_data["ad_unit_src"] = (
        grouped_data["slot_id"] + "_" + grouped_data["src"] + grouped_data["td_path"]
    )

    return grouped_data


class PriceRulesOptimizer:
    def __init__(self, data):
        results = []
        for case in np.unique(data["ad_unit_src"]):
            tmp = (
                data[data["ad_unit_src"] == case]
                .sort_values("DATE")
                .reset_index(drop=True)
            )
            tmp["cpm_shifted"] = tmp["cpm"].shift(1)
            tmp["coverage_shifted"] = tmp["coverage"].shift(1)
            results.append(tmp)

        results = pd.concat(results)
        self.data = results.dropna(axis=0).reset_index(drop=True)

    def getPriceRules(self):
        ohe = OneHotEncoder(drop=None, sparse=False)
        df_ohe = ohe.fit_transform(self.data[["weekDay", "slot_id", "src", "td_path"]])
        df_ohe = pd.DataFrame(df_ohe, columns=np.concatenate(ohe.categories_))

        data_to_split = pd.concat(
            [
                df_ohe,
                self.data[
                    [
                        "cpm_shifted",
                        "cpm",
                        "coverage_shifted",
                        "coverage",
                        "priceRule",
                        "cont",
                        "dolar",
                    ]
                ],
            ],
            axis=1,
        )

        dolar = getDolar()
        dolar = float(dolar["dolar"].iloc[-2])

        cpm, coverage, r2_coverage, r2_cpm = self.XGBoostFit(data_to_split, dolar=dolar)
        print("CPM PREDICTIONS RESULT: ", cpm)
        print("COVERAGE PREDICTIONS RESULT: ", coverage)

        predictions = coverage.merge(
            cpm, on=["adunit", "url", "src", "priceRule"], how="left"
        )
        predictions["adunitsrc"] = (
            predictions["adunit"] + "_" + predictions["url"] + "_" + predictions["src"]
        )
        predictions = predictions[
            ["adunitsrc", "adunit", "url", "src", "priceRule", "cpm", "coverage"]
        ]
        predictions["EstimatedRevenue"] = predictions["cpm"].astype(
            float
        ) * predictions["coverage"].astype(float)
        return predictions, round(r2_coverage, 4), round(r2_cpm, 4)

    def XGBoostFit(self, data_to_split, dolar):
        y_variable = "cpm"
        X_train, X_test, y_train, y_test = train_test_split(
            data_to_split.drop([y_variable, "coverage"], axis=1),
            data_to_split[[y_variable, "cont"]],
            test_size=0.2,
            random_state=42,
        )

        X_train = X_train.reindex(X_train.index.repeat(X_train.cont)).reset_index(
            drop=True
        )
        X_train = X_train.drop("cont", axis=1)
        X_test = X_test.drop("cont", axis=1)

        y_train = y_train.reindex(y_train.index.repeat(y_train.cont)).reset_index(
            drop=True
        )
        y_train = y_train[y_variable].values.reshape(-1, 1)
        y_test = np.concatenate(y_test[y_variable].values.reshape(-1, 1))

        model = xgboost.XGBRegressor()

        model.fit(X_train, y_train)

        pred = model.predict(X_test)

        MSE = mse(y_test, pred)
        R_squared_cpm = r2_score(y_test, pred)
        RMSE = np.sqrt(MSE)

        print("\nRMSE: ", np.round(RMSE, 4))
        print("R-Squared: ", np.round(R_squared_cpm, 4))

        self.space = self.createSpace(X_train, n_space=30)

        final_df = []
        for adunitsrc in np.unique(self.data["ad_unit_src"]):
            auxdf = self.data[self.data["ad_unit_src"] == adunitsrc]
            tmp = pd.DataFrame(
                np.zeros((len(self.space), X_train.shape[1])),
                columns=X_train.columns,
            )
            tmp[np.unique(auxdf["slot_id"])] = 1
            tmp[np.unique(auxdf["td_path"])] = 1
            tmp[np.unique(auxdf["src"])] = 1
            weekday = datetime.date.today() + datetime.timedelta(days=1)
            tmp[weekday.strftime("%A")] = 1
            tmp["cpm_shifted"] = auxdf["cpm"].iloc[-1]
            tmp["coverage_shifted"] = auxdf["coverage"].iloc[-1]
            tmp["priceRule"] = self.space
            tmp["dolar"] = dolar

            pred = model.predict(tmp)
            xg_results = pd.DataFrame([self.space, pred]).T
            xg_results.columns = ["priceRule", y_variable]
            xg_results["adunit"] = np.unique(auxdf["slot_id"])[0]
            xg_results["url"] = np.unique(auxdf["td_path"])[0]
            xg_results["src"] = np.unique(auxdf["src"])[0]
            final_df.append(xg_results)

        self.cpm_predictions = pd.concat(final_df)

        ######## COVERAGE MODEL ########

        y_variable = "coverage"
        data_to_split = data_to_split.reindex(
            data_to_split.index.repeat(data_to_split.cont)
        ).reset_index(drop=True)
        data_to_split = data_to_split.drop("cont", axis=1).reset_index(drop=True)

        X_train, X_test, y_train, y_test = train_test_split(
            data_to_split.drop(y_variable, axis=1),
            data_to_split[y_variable],
            test_size=0.2,
            random_state=42,
        )

        model = xgboost.XGBRegressor()

        model.fit(X_train, y_train)

        pred = model.predict(X_test)

        MSE = mse(y_test, pred)
        R_squared_coverage = r2_score(y_test, pred)
        RMSE = np.sqrt(MSE)

        print("\nRMSE: ", np.round(RMSE, 4))
        print("R-Squared: ", np.round(R_squared_coverage, 4))

        self.space = self.createSpace(X_train, n_space=30)

        final_df = []
        for adunitsrc in np.unique(self.data["ad_unit_src"]):
            auxdf = self.data[self.data["ad_unit_src"] == adunitsrc]
            tmp = pd.DataFrame(
                np.zeros((len(self.space), X_train.shape[1])),
                columns=X_train.columns,
            )
            tmp[np.unique(auxdf["slot_id"])] = 1
            tmp[np.unique(auxdf["td_path"])] = 1
            tmp[np.unique(auxdf["src"])] = 1
            tmp[weekday.strftime("%A")] = 1
            self.cpm_predictions["ad_unit_src"] = (
                self.cpm_predictions["adunit"]
                + "_"
                + self.cpm_predictions["src"]
                + self.cpm_predictions["url"]
            )
            tmp["cpm"] = self.cpm_predictions[
                self.cpm_predictions["ad_unit_src"] == adunitsrc
            ]["cpm"]
            tmp["cpm_shifted"] = auxdf["cpm"].iloc[-1]
            tmp["coverage_shifted"] = auxdf["coverage"].iloc[-1]
            tmp["priceRule"] = self.space
            tmp["dolar"] = dolar

            pred = model.predict(tmp)
            xg_results = pd.DataFrame([self.space, pred]).T
            xg_results.columns = ["priceRule", y_variable]
            xg_results["adunit"] = np.unique(auxdf["slot_id"])[0]
            xg_results["url"] = np.unique(auxdf["td_path"])[0]
            xg_results["src"] = np.unique(auxdf["src"])[0]
            final_df.append(xg_results)

        self.coverage_predictions = pd.concat(final_df)
        return (
            self.cpm_predictions,
            self.coverage_predictions,
            R_squared_coverage,
            R_squared_cpm,
        )

    def createSpace(self, X_train, n_space=30):
        start_space = round(X_train["priceRule"].min())
        end_space = round(X_train["priceRule"].max())
        if start_space == end_space:
            start_space = round(X_train["priceRule"].min(), 4)
            end_space = round(X_train["priceRule"].max(), 4)
        if start_space == 0:
            start_space = 1
        space = np.linspace(
            start=start_space,
            stop=end_space,
            num=n_space,
        )
        space = np.round(space)
        return space


def getDolar():  # sourcery skip: use-datetime-now-not-today
    today = str(datetime.datetime.today()).split(" ")[0].replace("-", "")
    dates = pd.date_range("2022-01-01", datetime.datetime.today())
    n = len(dates)

    url = f" https://economia.awesomeapi.com.br/USD-BRL/{n}?start_date=20220101&end_date={today}"
    request = requests.get(url)
    request_json = request.json()
    request_df = pd.DataFrame.from_dict(request_json)
    request_df["date"] = dates.astype(str)
    dolar = request_df[["date", "ask", "bid"]]
    dolar["dolar"] = dolar["ask"].shift(1)
    dolar = dolar.dropna()
    dolar = dolar[["date", "dolar"]]
    dolar.to_csv("./dolar.csv")
    return dolar


def auction_simulation(df):
    auction_medians = []
    auction_means = []
    for _ in range(5000):
        x = np.random.choice(df["BidPrice"], size=1000, replace=True)
        auction_medians.append(np.median(x))
        auction_means.append(x.mean())

    auction_medians = np.array(auction_medians)
    auction_means = np.array(auction_means)
    return auction_medians, auction_means
