import streamlit as st
import pandas as pd
from PIL import Image

# Layout
twt_logo = Image.open('app/images/twitter-logo.png')
st.set_page_config(
    page_title="Sentimental analysis", page_icon=twt_logo, layout="wide"
)

st.title("Investment Recommendation for the selected period")
st.header("Long or Short stocks")

@st.cache
def load_predicted_data():
    results = pd.read_csv("./data/data_model/results.csv",)
    return results


results = load_predicted_data()

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

# min_date = tweets["PostDate"].min()
# max_date = tweets["PostDate"].max()

# # filter start date
# start_date = st.date_input(
#     "**Select a start date:**",
#     min_value=min_date,
#     max_value=max_date,
#     value=min_date,
#     key="start_date",
# )
# # filter end date
# end_date = st.date_input(
#     "**Select an end date:**",
#     min_value=min_date,
#     max_value=max_date,
#     value=max_date,
#     key="end_date",
# )

# condition1 = start_date <= tweets["PostDate"]
# condition2 = tweets["PostDate"] <= end_date
# mask = condition1 & condition2
# filtered_tweets = tweets.loc[mask, :]

# mask = filtered_tweets["company"].isin(options)
# filtered_tweets = filtered_tweets.loc[mask, :]

# # we select all the tweets from 2017 to 2022
# tweet_list = filtered_tweets["TweetText"].tolist()
# # join all tweets into a single string
# tweet_string = " ".join(tweet_list)
st.dataframe(results)

results = results.reset_index(drop=False)
results = results.rename(columns={'index': 'companies'})

st.dataframe(results)
selected_stocks = results['companies'].isin(options)

st.dataframe(results.loc[selected_stocks])

# c1, c2, c3, c4 = st.columns(4)

# # with c1:
# #     st.metric(
# #         label=f"Investment recommendation on the portfolio:",
# #         value=str(results[results["sentiment"] == "Bullish"].shape[0]),
# #     )

# # with c2:
# #     st.metric(
# #         label=f"Return of the recommended investment:",
# #         value=str(filtered_tweets[filtered_tweets["sentiment"] == "Bearish"].shape[0]),
# #     )

# with c3:
#     st.metric(
#         label=f"Percentage of benefice or loss generated with our strategy:",
#         value=str(
#             round(results.loc[selected_stocks, "relative_return_pct"].mean()*100)
#         ) + "%"
#     )

# with c4:
#     st.metric(
#         label=f"Percentage of benefice or loss generated with an equipondered portfolio:",
#         value=str(
#             round(results.loc[selected_stocks, "to_compare_with_based"].mean()*100)
#         ) + "%"
#     )