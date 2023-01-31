# Libraries
import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import seaborn as sns
import plotly.express as px
from collections import Counter
import numpy as np

# Global Variables
DATE_COLUMN = "DATE"
DATA_PATH = "./../data/stocks_data.xlsx"
TWEETS_PATH = [
    "./../data_cleaned/webscraped_FMC_CORP.csv/part-00000-9fe4bf5d-f913-4d0c-a98a-8f1d088639ee-c000.csv",
    "./../data_cleaned/webscraped_WEYERHAEUSER_CO.csv/part-00000-17a4305d-9672-4ddf-87fc-d180dcf01612-c000.csv",
    "./../data_cleaned/webscraped_BP_PLC.csv/part-00000-60047cdf-7f10-49f8-932e-065bb69f747c-c000.csv",
]

# Layout
st.set_page_config(
    page_title="Tweets analysis for stocks", page_icon=":bar_chart:", layout="wide"
)
st.title("Tweets analysis for stocks 📈📉")

# Style
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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
    # we add fmc webscrapped data
    fmc_tweets = pd.read_csv(TWEETS_PATH[0])
    fmc_tweets["company"] = "FMC CORP"
    # we add wy webscrapped data
    wy_tweets = pd.read_csv(TWEETS_PATH[1])
    wy_tweets["company"] = "WEYERHAEUSER CO"
    # we add bp webscrapped data
    bp_tweets = pd.read_csv(TWEETS_PATH[2])
    bp_tweets["company"] = "BP PLC"
    tweets = pd.concat([fmc_tweets, wy_tweets, bp_tweets])
    tweets["PostDate"] = pd.to_datetime(tweets["PostDate"]).dt.date
    # we add a column with the length of each tweet
    tweets["tweet_length"] = tweets["TweetText"].apply(lambda x: len(x.split()))
    tweets["avg_word_length"] = tweets["TweetText"].apply(
        lambda x: sum(len(word) for word in x.split()) / len(x.split())
    )
    return returns, tweets


returns, tweets = load_data()

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
    "**Select your desired blockchains:**",
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

# Initialiser la variable des mots vides
stop_words = set(stopwords.words("english"))

# Create a function to check if a word starts with a number
def starts_with_number(word):
    return word[0].isdigit()


def most_common_words_tweets(filter_tw, number):
    # Create a list of all the words in the column 'TweetText'
    all_words = " ".join(filter_tw["TweetText"])

    # Split the list into individual words
    words = all_words.split()
    words = [
        word
        for word in words
        if (word.lower() not in stop_words) and (not starts_with_number(word))
    ]

    # Use the pandas method 'value_counts' to get the frequency of each word
    word_freq = pd.Series(words).value_counts()
    # Plot the top 20 most common words
    word_freq[:20].sort_values(ascending=True).plot.barh()

    fig = px.bar(word_freq.reset_index(), x="index", y=0, text=0)
    fig.update_layout(
        title=f"Most Common Words in the Tweets for {options[number]}",
        xaxis_title="Words",
        yaxis_title="Frequency",
    )
    st.plotly_chart(fig)


def length_of_words(filter_tw, number):
    fig = px.histogram(filter_tw, x="avg_word_length", nbins=20)
    fig.update_layout(
        xaxis_title="Average Word Length",
        yaxis_title="Frequency",
        title=f"Distribution of Average Word Length in Tweets for {options[number]} from {start_date} to {end_date}",
    )
    st.plotly_chart(fig)


def treemap(filter_tw, number):
    tweet_text = filter_tw["TweetText"].str.cat(sep=" ")

    # split the words and remove stopwords
    filtered_words = [
        word
        for word in tweet_text.split()
        if (word.lower() not in stop_words) and (not starts_with_number(word))
    ]

    # get the top 20 most common words
    common_words = Counter(filtered_words).most_common(20)
    # Create a DataFrame from the list of common words
    df = pd.DataFrame(common_words, columns=["word", "count"])

    # create the treemap
    fig = px.treemap(
        df,
        path=["word"],
        values="count",
        title=f"Treemap of most common words for {options[number]}",
        color="count",
        color_continuous_scale="reds",
    )
    st.plotly_chart(fig)


def word_donut_plot(df, number):
    all_words = " ".join(df["TweetText"]).split()

    # Filter out the stop words and words starting with numbers
    all_words = [
        word
        for word in all_words
        if (word.lower() not in stop_words) and (not starts_with_number(word))
    ]

    # Count the number of occurrences of each word
    word_counts = Counter(all_words)

    # Get the unique words and their counts
    unique_words = dict(word_counts)

    # Sort the dictionary by values (word counts) in descending order
    unique_words = dict(
        sorted(unique_words.items(), key=lambda item: item[1], reverse=True)
    )

    # Keep the first n items where n is the number of items you want to keep
    unique_words = dict(list(unique_words.items())[:number])

    # Plot the donut chart
    fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))

    data = list(unique_words.values())

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(
        xycoords="data",
        textcoords="data",
        arrowprops=dict(arrowstyle="-"),
        bbox=bbox_props,
        zorder=0,
        va="center",
    )

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        kw["va"] = "center"
        ax.annotate(
            list(unique_words.keys())[i],
            xy=(x, y),
            xytext=(1.7 * np.sign(x), 1.7 * y),
            horizontalalignment=horizontalalignment,
            **kw,
        )

    ax.set_title(f"Unique words in tweets for {options[number]}")

    plt.show()

    st.plotly_chart(fig)


if len(options) == 0:
    st.warning("Please select at least one stock to see the metrics.")

elif len(options) == 1:
    mask = filtered_tweets["company"] == options[0]
    filtered_tweets = filtered_tweets.loc[mask, :]
    st.subheader(f"Analytics for {options[0]} from {start_date} to {end_date}")
    st.metric(
        label=f"Number of tweets for {options[0]}:", value=str(filtered_tweets.shape[0])
    )
    #     st.metric(label='**Total Returns**', value=str(returns[options].map('{:,.0f}'.format).values[0]))
    #     st.metric(label='**Average Transactions/Block**', value=str(returns[options].map('{:,.0f}'.format).values[0]))

    # we select all the tweets from 2017 to 2022
    tweet_list = filtered_tweets["TweetText"].tolist()
    # join all tweets into a single string
    tweet_string = " ".join(tweet_list)

    # # we have decided to remove the name of the company because is our keyword
    # tweet_string = tweet_string.replace("weyerhaeuser", "").replace("co", "")

    # create the word cloud
    wordcloud = WordCloud(stopwords=stop_words).generate(tweet_string)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title(f"Wordcloud for {options[0]} from {start_date} to {end_date}")
    plt.axis("off")
    plt.show()

    def wordcloud_stock():
        st.pyplot(plt)

    wordcloud_stock()

    # frequency plot
    def frequency_tweets_length_stock():
        sns.set_style("darkgrid")
        sns.displot(filtered_tweets["tweet_length"], bins=20)
        plt.title(f"Tweet frequency length for {options[0]}")
        plt.xlabel("Tweet Length")
        plt.ylabel("Number of Tweets")
        plt.show()
        st.pyplot(plt)

    frequency_tweets_length_stock()

    length_of_words(filtered_tweets, 0)
    most_common_words_tweets(filtered_tweets, 0)
    treemap(filtered_tweets, 0)

elif len(options) == 2:
    st.subheader(f'Analytics for {", ".join(options)} from {start_date} to {end_date}')
    c1, c2 = st.columns(2)

    with c1:
        mask_1 = filtered_tweets["company"] == options[0]
        filtered_tweets_1 = filtered_tweets.loc[mask_1, :]
        st.metric(
            label=f"Number of tweets for {options[0]}:",
            value=str(filtered_tweets_1.shape[0]),
        )

        # we select all the tweets from 2017 to 2022
        tweet_list = filtered_tweets_1["TweetText"].tolist()
        # join all tweets into a single string
        tweet_string = " ".join(tweet_list)

        # frequency plot
        def frequency_tweets_length_stock():
            sns.set_style("darkgrid")
            sns.displot(filtered_tweets_1["tweet_length"], bins=20)
            plt.title(f"Tweet frequency length for {options[0]}")
            plt.xlabel("Tweet Length")
            plt.ylabel("Number of Tweets")
            plt.show()
            st.pyplot(plt)

        frequency_tweets_length_stock()

        # create the word cloud
        wordcloud = WordCloud(stopwords=stop_words).generate(tweet_string)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.title(f"Wordcloud for {options[0]} from {start_date} to {end_date}")
        plt.axis("off")
        plt.show()

        def wordcloud_stock():
            st.pyplot(plt)

        wordcloud_stock()

    with c2:
        mask_2 = filtered_tweets["company"] == options[1]
        filtered_tweets_2 = filtered_tweets.loc[mask_2, :]
        st.metric(
            label=f"Number of tweets for {options[1]}:",
            value=str(filtered_tweets_2.shape[0]),
        )

        # we select all the tweets from 2017 to 2022
        tweet_list = filtered_tweets_2["TweetText"].tolist()
        # join all tweets into a single string
        tweet_string = " ".join(tweet_list)

        # frequency plot
        def frequency_tweets_length_stock():
            sns.set_style("darkgrid")
            sns.displot(filtered_tweets_2["tweet_length"], bins=20)
            plt.title(f"Tweet frequency length for {options[1]}")
            plt.xlabel("Tweet Length")
            plt.ylabel("Number of Tweets")
            plt.show()
            st.pyplot(plt)

        frequency_tweets_length_stock()

        # create the word cloud
        wordcloud = WordCloud(stopwords=stop_words).generate(tweet_string)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.title(f"Wordcloud for {options[0]} from {start_date} to {end_date}")
        plt.axis("off")
        plt.show()

        def wordcloud_stock():
            st.pyplot(plt)

        wordcloud_stock()

    length_of_words(filtered_tweets_1, 0)
    length_of_words(filtered_tweets_2, 1)

    most_common_words_tweets(filtered_tweets_1, 0)
    most_common_words_tweets(filtered_tweets_2, 1)

    treemap(filtered_tweets_1, 0)
    treemap(filtered_tweets_2, 1)

elif len(options) == 3:
    st.subheader(f'Analytics for {", ".join(options)} from {start_date} to {end_date}')
    c1, c2, c3 = st.columns(3)

    with c1:
        mask_1 = filtered_tweets["company"] == options[0]
        filtered_tweets_1 = filtered_tweets.loc[mask_1, :]
        st.metric(
            label=f"Number of tweets for {options[0]}:",
            value=str(filtered_tweets_1.shape[0]),
        )

        # we select all the tweets from 2017 to 2022
        tweet_list = filtered_tweets_1["TweetText"].tolist()
        # join all tweets into a single string
        tweet_string = " ".join(tweet_list)

        # frequency plot
        def frequency_tweets_length_stock():
            sns.set_style("darkgrid")
            sns.displot(filtered_tweets_1["tweet_length"], bins=20)
            plt.title(f"Tweet frequency length for {options[0]}")
            plt.xlabel("Tweet Length")
            plt.ylabel("Number of Tweets")
            plt.show()
            st.pyplot(plt)

        frequency_tweets_length_stock()

        # create the word cloud
        wordcloud = WordCloud(stopwords=stop_words).generate(tweet_string)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.title(f"Wordcloud for {options[0]} from {start_date} to {end_date}")
        plt.axis("off")
        plt.show()

        def wordcloud_stock():
            st.pyplot(plt)

        wordcloud_stock()

    with c2:
        mask_2 = filtered_tweets["company"] == options[1]
        filtered_tweets_2 = filtered_tweets.loc[mask_2, :]
        st.metric(
            label=f"Number of tweets for {options[1]}:",
            value=str(filtered_tweets_2.shape[0]),
        )

        # we select all the tweets from 2017 to 2022
        tweet_list = filtered_tweets_2["TweetText"].tolist()
        # join all tweets into a single string
        tweet_string = " ".join(tweet_list)

        # frequency plot
        def frequency_tweets_length_stock():
            sns.set_style("darkgrid")
            sns.displot(filtered_tweets_2["tweet_length"], bins=20)
            plt.title(f"Tweet frequency length for {options[1]}")
            plt.xlabel("Tweet Length")
            plt.ylabel("Number of Tweets")
            plt.show()
            st.pyplot(plt)

        frequency_tweets_length_stock()

        # create the word cloud
        wordcloud = WordCloud(stopwords=stop_words).generate(tweet_string)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.title(f"Wordcloud for {options[1]} from {start_date} to {end_date}")
        plt.axis("off")
        plt.show()

        def wordcloud_stock():
            st.pyplot(plt)

        wordcloud_stock()

    with c3:
        mask_3 = filtered_tweets["company"] == options[2]
        filtered_tweets_3 = filtered_tweets.loc[mask_3, :]
        st.metric(
            label=f"Number of tweets for {options[2]}:",
            value=str(filtered_tweets_3.shape[0]),
        )

        # we select all the tweets from 2017 to 2022
        tweet_list = filtered_tweets_3["TweetText"].tolist()
        # join all tweets into a single string
        tweet_string = " ".join(tweet_list)

        # frequency plot
        def frequency_tweets_length_stock():
            sns.set_style("darkgrid")
            sns.displot(filtered_tweets_3["tweet_length"], bins=20)
            plt.title(f"Tweet frequency length for {options[2]}")
            plt.xlabel("Tweet Length")
            plt.ylabel("Number of Tweets")
            plt.show()
            st.pyplot(plt)

        frequency_tweets_length_stock()

        def wordcloud_stock():
            # create the word cloud
            wordcloud = WordCloud(stopwords=stop_words).generate(tweet_string)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.title(f"Wordcloud for {options[2]} from {start_date} to {end_date}")
            plt.axis("off")
            plt.show()
            st.pyplot(plt)

        wordcloud_stock()

    length_of_words(filtered_tweets_1, 0)
    length_of_words(filtered_tweets_2, 1)
    length_of_words(filtered_tweets_3, 2)

    most_common_words_tweets(filtered_tweets_1, 0)
    most_common_words_tweets(filtered_tweets_2, 1)
    most_common_words_tweets(filtered_tweets_3, 2)

    treemap(filtered_tweets_1, 0)
    treemap(filtered_tweets_2, 1)
    treemap(filtered_tweets_3, 2)

    word_donut_plot(filtered_tweets_1, 0)
    word_donut_plot(filtered_tweets_2, 1)
    word_donut_plot(filtered_tweets_3, 2)
