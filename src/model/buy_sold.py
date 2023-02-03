import pandas

class PortfolioModel:
    def __init__(self, path:str, returns_path:str) -> None:
        self.path = path
        self.returns_path = returns_path

    def read_data(self):
        self.returns = pandas.read_excel(self.returns_path, sheet_name="Returns", header=[5, 6]).T.iloc[2:, :]
        self.df = pandas.read_csv(self.path)

    def formatting(self) -> None:
        """Formatting the dates and encoding sentiment columns positive or bullish -> 1, negative or bearish -> -1, neutral -> 0"""
        self.df['PostDate'] = pandas.to_datetime(self.df['PostDate'].apply(lambda x: x[:-3]))

        # add a column for the year and month
        self.df['year'] = self.df['PostDate'].dt.year
        self.df['month'] = self.df['PostDate'].dt.month

        # formatting sentiments
        self.df['sentiment'] = self.df['sentiment'].map({'Bullish': 1, 'Bearish': -1})
        self.df['sentiment_base'] = self.df['sentiment_base'].map({'positive': 1, 'neutral': 0, 'negative': -1})

        # formatting returns 
        self.returns = self.returns.rename(columns=self.returns.iloc[0])
        self.returns = self.returns.iloc[2:]
        upercase = lambda x: str(x).upper()
        self.returns.rename(upercase, axis="columns", inplace=True)
        self.returns.reset_index(inplace=True)
        self.returns.rename(columns={"level_0": "DATE1", "level_1": "DATE"}, inplace=True)
        self.returns.drop(columns="DATE1", inplace=True)
        self.returns["DATE"] = pandas.to_datetime(self.returns["DATE"]).dt.date
        
        # we apply to convert the percentage on indices
        except_column = 'DATE'
        selected_columns = [col for col in self.returns.columns if col != except_column]
        result = self.returns[selected_columns].apply(lambda x: x/100 + 1, axis=1)
        self.returns = pandas.concat([self.returns[except_column], result], axis=1)

    def positive_ratio(self) -> pandas.DataFrame:
        # group the data by year and month
        grouped = self.df.groupby(['year', 'month', 'company'])

        # count the number of positive and negative tweets for each year and month
        sentiment_positive_tweets_by_month = grouped['sentiment'].apply(lambda x: (x == 1).sum())
        sentiment_negative_tweets_by_month = grouped['sentiment'].apply(lambda x: (x == -1).sum())
        sentiment_base_positive_tweets_by_month = grouped['sentiment_base'].apply(lambda x: (x == 1).sum())
        sentiment_base_neutral_tweets_by_month = grouped['sentiment_base'].apply(lambda x: (x == 0).sum())
        sentiment_base_negative_tweets_by_month = grouped['sentiment_base'].apply(lambda x: (x == -1).sum())

        # calculate the ratio of positive and negative tweets for each year and month
        positive_ratios_by_month = (sentiment_base_positive_tweets_by_month + sentiment_positive_tweets_by_month) / (sentiment_positive_tweets_by_month + sentiment_negative_tweets_by_month + sentiment_base_positive_tweets_by_month + sentiment_base_neutral_tweets_by_month + sentiment_base_negative_tweets_by_month)
        
        # formatting
        positive_ratios_by_month = positive_ratios_by_month.reset_index()
        positive_ratios_by_month.rename(columns={0:'positive_ratio'}, inplace=True)
        positive_ratios_by_month['yearmonth'] = positive_ratios_by_month['year'].astype(str) + '-' + positive_ratios_by_month['month'].astype(str).str.zfill(2)
        return positive_ratios_by_month

    def short_or_long(self):
        positive_ratios_by_month = self.positive_ratio()
        date_index = positive_ratios_by_month['yearmonth'].unique().tolist()
        unique_companies = positive_ratios_by_month['company'].unique().tolist()
        self.shortlongdf = pandas.DataFrame(index=date_index)
        for company in unique_companies:
            # selection of the company
            mask = positive_ratios_by_month['company'] == company
            stock_ratios = positive_ratios_by_month.loc[mask]

            # selection of the period
            stock_ratios.loc[:, 'positive_ratio_shifted'] = stock_ratios['positive_ratio'].shift(1)
            stock_ratios.loc[:, 'buy_or_sell'] = (stock_ratios['positive_ratio_shifted'] - 0.5) * 2
            stock_ratios.set_index('yearmonth', inplace=True)
            # saving info in a dataframe
            self.shortlongdf[company] = stock_ratios['buy_or_sell']

    def cumulative_sum(self, col_name):
        cumulative_sum = 0
        cumulative_sum_list = []
        self.shortlongdf.fillna(0, inplace=True)
        for value in self.shortlongdf[col_name]:
            cumulative_sum += value
            if cumulative_sum < 0:
                cumulative_sum = 0
            cumulative_sum_list.append(cumulative_sum)
        self.shortlongdf[f"{col_name}_cumulative_sum"] = cumulative_sum_list


    def cumsum_per_stock(self):
        for col_name in self.shortlongdf.columns.to_list():
            self.cumulative_sum(col_name)
        print(self.shortlongdf.head())

    def launch(self):
        self.read_data()
        self.formatting()
        self.short_or_long()
        self.cumsum_per_stock()

if __name__ == "__main__":
    path = "./../../data/data_model/all_data.csv"
    returns_path = "./../../data/stocks_data.xlsx"
    model = PortfolioModel(path=path, returns_path=returns_path).launch()