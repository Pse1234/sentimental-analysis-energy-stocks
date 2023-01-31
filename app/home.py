import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# from Home import load_data

# Global Variables
DATE_COLUMN = "DATE"
DATA_PATH = "./../data/stocks_data.xlsx"
RAW_TWEETS_PATH = [
    "./../data/webscraped_FMC_CORP.csv",
    "./../data/webscraped_WEYERHAEUSER_CO.csv",
    "./../data/webscraped_BP_PLC.csv",
]

# Layout
st.set_page_config(page_title="Home", page_icon=":bar_chart:", layout="wide")
st.title("Does Twitter have influence in stocks?")


st.markdown(
    """
 * Use the menu at left to select data and set plot parameters for analysis
"""
)
c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
stock_list = [
    "bp",
    "exxonmobil",
    "diamondbacks",
    "totalenergies",
    "upm",
    "chevron",
    "newmont",
]
for i, stock in enumerate(stock_list):
    logo_path = f"images/{stock}-logo.png"
    if i == 0:
        c1.image(Image.open(logo_path))
    elif i == 1:
        c2.image(Image.open(logo_path))
    elif i == 2:
        c3.image(Image.open(logo_path))
    elif i == 3:
        c4.image(Image.open(logo_path))
    elif i == 4:
        c5.image(Image.open(logo_path))
    elif i == 5:
        c6.image(Image.open(logo_path))
    elif i == 6:
        c7.image(Image.open(logo_path))


st.subheader("Presentation Twitter")
st.write(
    """    
    Twitter is a social media platform that allows users to post short messages, called tweets, which can contain text, images, and videos. These tweets can be viewed by other users, who can also interact with them by replying, re-tweeting, or liking them.
    From a web scraping point of view, Twitter can be accessed through its website, which is built using a combination of HTML, CSS, and JavaScript. To scrape data from Twitter, one would need to send HTTP requests to the Twitter server, which would return the HTML of the webpage. This HTML can then be parsed using a library such as Selenium to extract the desired data, such as tweets, 
    user information, and follower counts.
    It's important to note that scraping data from Twitter is against the company's terms of service, and it is not recommended to scrape the data without permission. Also, Twitter has some security mechanisms that prevent scraping like CAPTCHA, IP blocking and rate limiting
    """
)

st.subheader("Example of webscrapped dataset")


@st.cache
def load_data():
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
    fmc_tweets = pd.read_csv(RAW_TWEETS_PATH[0])
    fmc_tweets["company"] = "FMC CORP"
    wy_tweets = pd.read_csv(RAW_TWEETS_PATH[1])
    wy_tweets["company"] = "WEYERHAEUSER CO"
    tweets = pd.concat([fmc_tweets, wy_tweets])
    tweets["PostDate"] = pd.to_datetime(tweets["PostDate"]).dt.date
    # we add a column with the length of each tweet
    tweets["tweet_length"] = tweets["TweetText"].apply(lambda x: len(x.split()))
    return returns, tweets


returns, tweets = load_data()
st.dataframe(tweets.head())

st.subheader("Methodology")
st.write(
    """    
    The webscrapped dataset is then preprocessed and cleaned by a script in the folder. We're then doing an exploratory analysis and finally implementing a sentiment analysis model.
    We're implementing two pre-trained models to our webscrapped and preprocessed dataframe : 

    The first one is "tarnformnet/Stock-Sentiment-BERT" model, which is a BERT-based model trained on stock market-related 
    tweets for sentiment analysis. The model is fine-tuned on a dataset of tweets related to publicly traded companies and is 
    able to predict the sentiment of tweets as either positive, negative, or neutral.

    The second one is  a pre-trained language model called "finBERT" that was developed by Prosus AI and made available through 
    the Hugging Face library. It is a BERT model fine-tuned on financial domain-specific data, trained to do tasks such as 
    sentiment analysis, named entity recognition, and question answering. The model is trained on a large dataset of financial 
    articles, news and SEC filings. The finBERT can be fine-tuned on specific financial tasks, and it can be used for a variety 
    of NLP tasks including sentiment analysis, named entity recognition, and question answering. 

    This aggregated model has for goal to guide us for decision in stocks, like bear or bull. 
    """
)

st.subheader("Results")

st.subheader("About us")
# -- Aknowledgments
c1, c2 = st.columns(2)
with c1:
    st.info(
        "**Data Scientists Linkedin: [@JAGS](https://www.linkedin.com/in/jagarciasanchez) [@Sarra](https://www.linkedin.com/in/sarrabenyahia/)**",
        icon="💡",
    )
with c2:
    st.info(
        "**GitHub: [@JAGS](https://github.com/Pse1234) [@Sarra](https://github.com/sarrabenyahia)**",
        icon="💻",
    )
