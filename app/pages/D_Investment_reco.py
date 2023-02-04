import streamlit as st
import pandas as pd
from PIL import Image

# Global Variables
DATE_COLUMN = "DATE"
DATA_PATH = "./data/stocks_data.xlsx"
TWEETS_PREDICTED_PATH = [
    "./data/data_model/webscraped_FMC_CORP.csv",
    "./data/data_model/webscraped_WEYERHAEUSER_CO.csv",
    "./data/data_model/webscraped_BP_PLC.csv",
]

# Layout
twt_logo = Image.open('app/images/twitter-logo.png')
st.set_page_config(
    page_title="Sentimental analysis", page_icon=twt_logo, layout="wide"
)

st.title("Investment Recommendation for the selected period")
st.header("Long or Short stocks")

@st.cache
def load_predicted_data():
    returns = pd.read_excel(DATA_PATH, sheet_name="Returns", header=[5, 6]).T.iloc[
        2:, :
    ]
    returns = returns.rename(columns=returns.iloc[0])
    returns = returns.iloc[2:]
    upercase = lambda x: str(x).upper()
    returns.rename(upercase, axis="columns", inplace=True)
    returns.reset_index(inplace=True)
    returns.rename(columns={"level_0": "DATE1", "level_1": "DATE"}, inplace=True)
    returns.drop(columns="DATE1", inplace=True)
    returns[DATE_COLUMN] = pd.to_datetime(returns[DATE_COLUMN]).dt.date
    # we add fmc webscrapped data
    fmc_tweets = pd.read_csv(TWEETS_PREDICTED_PATH[0])
    fmc_tweets["company"] = "FMC CORP"
    # we add wy webscrapped data
    wy_tweets = pd.read_csv(TWEETS_PREDICTED_PATH[1])
    wy_tweets["company"] = "WEYERHAEUSER CO"
    # we add bp webscrapped data
    bp_tweets = pd.read_csv(TWEETS_PREDICTED_PATH[2])
    bp_tweets["company"] = "BP PLC"
    tweets = pd.concat([fmc_tweets, wy_tweets, bp_tweets])
    tweets["PostDate"] = pd.to_datetime(tweets["PostDate"]).dt.date
    # we add a column with the length of each tweet
    tweets["tweet_length"] = tweets["TweetText"].apply(lambda x: len(x.split()))
    return returns, tweets


returns, tweets = load_predicted_data()

stocklist = [
    "BP PLC",
    "FMC CORP",
    "WEYERHAEUSER CO",
]

df_columns_list = [
    "BP/ LN Equity",
    "FMC US Equity",
    "WY US Equity",
]

search_dictio = {}
for i, k in enumerate(df_columns_list):
    search_dictio[stocklist[i]] = k


# Filter the stocks
options = st.multiselect(
    "**Select your desired stocks:**",
    options=stocklist,
    default=None,
    key="macro_options",
)


min_date = tweets["PostDate"].min()
max_date = tweets["PostDate"].max()

# filter start date
start_date = st.date_input(
    "**Select a start date:**",
    min_value=min_date,
    max_value=max_date,
    value=min_date,
    key="start_date",
)
# filter end date
end_date = st.date_input(
    "**Select an end date:**",
    min_value=min_date,
    max_value=max_date,
    value=max_date,
    key="end_date",
)

condition1 = start_date <= tweets["PostDate"]
condition2 = tweets["PostDate"] <= end_date
mask = condition1 & condition2
filtered_tweets = tweets.loc[mask, :]

mask = filtered_tweets["company"].isin(options)
filtered_tweets = filtered_tweets.loc[mask, :]

# we select all the tweets from 2017 to 2022
tweet_list = filtered_tweets["TweetText"].tolist()
# join all tweets into a single string
tweet_string = " ".join(tweet_list)