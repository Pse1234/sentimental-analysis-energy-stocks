import pandas


class PortfolioModel:
    def __init__(self, path: str, returns_path: str) -> None:
        self.path = path
        self.returns_path = returns_path

    def read_data(self):
        self.returns = pandas.read_excel(
            self.returns_path, sheet_name="Returns", header=[5, 6]
        ).T.iloc[2:, :]
        self.df = pandas.read_csv(self.path)

    def formatting(self) -> None:
        """Formatting the dates and encoding sentiment columns positive or bullish -> 1, negative or bearish -> -1, neutral -> 0"""

        self.df["PostDate"] = self.df["PostDate"].astype(str).apply(lambda x: x[:-3])
        self.df["PostDate"] = pandas.to_datetime(self.df["PostDate"])

        # drop rows with NaN values in the "PostDate" column
        self.df.dropna(subset=["PostDate"], inplace=True)
    
        # add a column for the year and month
        self.df["year"] = self.df["PostDate"].dt.year
        self.df["month"] = self.df["PostDate"].dt.month

        # formatting sentiments
        self.df["sentiment"] = self.df["sentiment"].map({"Bullish": 1, "Bearish": -1})
        self.df["sentiment_base"] = self.df["sentiment_base"].map(
            {"positive": 1, "neutral": 0, "negative": -1}
        )

        # formatting returns
        self.returns = self.returns.rename(columns=self.returns.iloc[0])
        self.returns = self.returns.iloc[2:]
        upercase = lambda x: str(x).upper()
        self.returns.rename(upercase, axis="columns", inplace=True)
        self.returns.reset_index(inplace=True)
        self.returns.rename(
            columns={"level_0": "DATE1", "level_1": "DATE"}, inplace=True
        )
        self.returns.drop(columns="DATE1", inplace=True)
        self.returns["DATE"] = pandas.to_datetime(self.returns["DATE"]).dt.date

        # we apply to convert the percentage on indices
        except_column = "DATE"
        selected_columns = [col for col in self.returns.columns if col != except_column]
        result = self.returns[selected_columns].apply(lambda x: x / 100 + 1, axis=1)
        self.returns = pandas.concat([self.returns[except_column], result], axis=1)
        self.returns["DATE"] = pandas.to_datetime(self.returns["DATE"])
        self.returns["year"] = self.returns["DATE"].dt.year
        self.returns["month"] = self.returns["DATE"].dt.month
        self.returns["yearmonth"] = (
            self.returns["year"].astype(str)
            + "-"
            + self.returns["month"].astype(str).str.zfill(2)
        )
        result_on_pct = self.returns[selected_columns].apply(lambda x: x / 100, axis=1)
        self.returns_on_pct = pandas.concat([self.returns[except_column], result_on_pct], axis=1)
        self.returns_on_pct["DATE"] = pandas.to_datetime(self.returns["DATE"])
        self.returns_on_pct["year"] = self.returns_on_pct["DATE"].dt.year
        self.returns_on_pct["month"] = self.returns_on_pct["DATE"].dt.month
        self.returns_on_pct["yearmonth"] = (
            self.returns_on_pct["year"].astype(str)
            + "-"
            + self.returns_on_pct["month"].astype(str).str.zfill(2)
        )

    def positive_ratio(self) -> pandas.DataFrame:
        # group the data by year and month
        grouped = self.df.groupby(["year", "month", "company"])

        # count the number of positive and negative tweets for each year and month
        sentiment_positive_tweets_by_month = grouped["sentiment"].apply(
            lambda x: (x == 1).sum()
        )
        sentiment_negative_tweets_by_month = grouped["sentiment"].apply(
            lambda x: (x == -1).sum()
        )
        sentiment_base_positive_tweets_by_month = grouped["sentiment_base"].apply(
            lambda x: (x == 1).sum()
        )
        sentiment_base_neutral_tweets_by_month = grouped["sentiment_base"].apply(
            lambda x: (x == 0).sum()
        )
        sentiment_base_negative_tweets_by_month = grouped["sentiment_base"].apply(
            lambda x: (x == -1).sum()
        )

        # calculate the ratio of positive and negative tweets for each year and month
        positive_ratios_by_month = (
            sentiment_base_positive_tweets_by_month + sentiment_positive_tweets_by_month
        ) / (
            sentiment_positive_tweets_by_month
            + sentiment_negative_tweets_by_month
            + sentiment_base_positive_tweets_by_month
            + sentiment_base_neutral_tweets_by_month
            + sentiment_base_negative_tweets_by_month
        )

        # formatting
        positive_ratios_by_month = positive_ratios_by_month.reset_index()
        positive_ratios_by_month.rename(columns={0: "positive_ratio"}, inplace=True)
        positive_ratios_by_month["yearmonth"] = (
            positive_ratios_by_month["year"].astype(str)
            + "-"
            + positive_ratios_by_month["month"].astype(str).str.zfill(2)
        )
        return positive_ratios_by_month

    def short_or_long(self):
        """new dataframe with buy or sell at t"""
        positive_ratios_by_month = self.positive_ratio()
        date_index = positive_ratios_by_month["yearmonth"].unique().tolist()
        unique_companies = positive_ratios_by_month["company"].unique().tolist()
        self.shortlongdf = pandas.DataFrame(index=date_index)
        for company in unique_companies:
            # selection of the company
            mask = positive_ratios_by_month["company"] == company
            stock_ratios = positive_ratios_by_month.loc[mask]

            # selection of the period
            stock_ratios.loc[:, "positive_ratio_shifted"] = stock_ratios[
                "positive_ratio"
            ].shift(1)
            stock_ratios.loc[:, "buy_or_sell"] = (
                stock_ratios["positive_ratio_shifted"] - 0.5
            ) * 2
            stock_ratios.set_index("yearmonth", inplace=True)
            # saving info in a dataframe
            self.shortlongdf[company] = stock_ratios["buy_or_sell"]

    def calculating_stock(self, company_name, stock_name):
        """ we calcule for each stock the returns and the stock at t: we are going to use self.returns and self.shortlongdf"""

        cumulative_sum = 0
        cumulative_sum_list = []
        self.shortlongdf.fillna(0, inplace=True)
        assert self.returns.shape[0] == self.shortlongdf.shape[0], "Returns dataframe has not the same length as the webscrapped data"
        for i, value in enumerate(self.shortlongdf[company_name]):
            cumulative_sum += value
            if cumulative_sum < 0:
                cumulative_sum = 0
            cumulative_sum = cumulative_sum * self.returns_on_pct.loc[i, stock_name]
            cumulative_sum_list.append(cumulative_sum)
        self.shortlongdf[f"{company_name}_cumulative_sum"] = cumulative_sum_list

    def cumsum_of_returns_per_stock(self):
        """cumsum for all stocks"""
        self.stocklist = [
            "BP PLC",
            "FMC CORP",
            "WEYERHAEUSER CO",
            "ALTAGAS LTD",
            "BHP GROUP",
            "INTERNATIONAL PAPER CO",
            "S&P 500 ENERGY INDEX",
            "STORA ENSO",
            "WILMAR INTERNATIONAL LTD",
            "TOTALENERGIES SE",
        ]

        self.df_columns_list = [
            "BP/ LN Equity",
            "FMC US Equity",
            "WY US Equity",
            "ALA CT Equity",
            "BHP US Equity",
            "IP US Equity",
            "S5ENRS Index",
            "STERV FH Equity",
            "WIL SP Equity",
            "TTE FP Equity",
        ]

        self.search_dictio = {}
        for i, k in enumerate(self.df_columns_list):
            self.search_dictio[self.stocklist[i]] = k

        for col_name in self.shortlongdf.columns.to_list():
            self.calculating_stock(col_name, stock_name = self.search_dictio.get(col_name).upper())

    def results_per_stock(self):
        self.printing_results = pandas.DataFrame()
        for col in self.stocklist:
            self.printing_results.loc[col, 'total_investment'] = self.shortlongdf[self.shortlongdf[col] > 0][col].sum()
            self.printing_results.loc[col, 'total_return'] = self.shortlongdf[col+'_cumulative_sum'].sum()
            self.printing_results.loc[col, 'market_results'] = self.returns[self.search_dictio.get(col).upper()].prod() -1
        self.printing_results['strategy_results'] = self.printing_results['total_return'] / self.printing_results['total_investment']
        
        self.printing_results.to_csv("./../../data/data_model/results.csv")
        self.shortlongdf.to_csv("./../../data/data_model/todo.csv")
        print(self.shortlongdf)

    def launch(self):
        # reading returns and analyse data NLP
        self.read_data()
        # formatting the data
        self.formatting()
        # returning a dataframe with if short or long stocks by date
        self.short_or_long()

        self.cumsum_of_returns_per_stock()
        self.results_per_stock()


if __name__ == "__main__":
    path = "./../../data/data_model/all_data.csv"
    returns_path = "./../../data/stocks_data.xlsx"
    model = PortfolioModel(path=path, returns_path=returns_path).launch()
