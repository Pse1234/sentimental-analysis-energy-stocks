import pandas

class PortfolioModel:
    def __init__(self, df:pandas.DataFrame) -> None:
        self.df = df

    def formatting(self) -> None:
        """Formatting the dates and encoding sentiment columns positive or bullish -> 1, negative or bearish -> -1, neutral -> 0"""
        self.df['PostDate'] = pandas.to_datetime(self.df['PostDate'].apply(lambda x: x[:-3]))

        # add a column for the year and month
        self.df['year'] = self.df['PostDate'].dt.year
        self.df['month'] = self.df['PostDate'].dt.month

        # formatting sentiments
        self.df['sentiment'] = self.df['sentiment'].map({'Bullish': 1, 'Bearish': -1})
        self.df['sentiment_base'] = self.df['sentiment_base'].map({'positive': 1, 'neutral': 0, 'negative': -1})

    def positive_ratio(self) -> pandas.Series:
        # group the data by year and month
        grouped = self.df.groupby(['year', 'month'])

        # count the number of positive and negative tweets for each year and month
        sentiment_positive_tweets_by_month = grouped['sentiment'].apply(lambda x: (x == 1).sum())
        sentiment_negative_tweets_by_month = grouped['sentiment'].apply(lambda x: (x == -1).sum())
        sentiment_base_positive_tweets_by_month = grouped['sentiment_base'].apply(lambda x: (x == 1).sum())
        sentiment_base_neutral_tweets_by_month = grouped['sentiment_base'].apply(lambda x: (x == 0).sum())
        sentiment_base_negative_tweets_by_month = grouped['sentiment_base'].apply(lambda x: (x == -1).sum())

        # calculate the ratio of positive and negative tweets for each year and month
        positive_ratios_by_month = (sentiment_base_positive_tweets_by_month + sentiment_positive_tweets_by_month) / (sentiment_positive_tweets_by_month + sentiment_negative_tweets_by_month + sentiment_base_positive_tweets_by_month + sentiment_base_neutral_tweets_by_month + sentiment_base_negative_tweets_by_month)
        return positive_ratios_by_month

    def short(self):
        if self.df['sentiment'] and self.df['sentiment_base']:
            pass
    def long(self):
        pass