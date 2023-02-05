# Overperforming 58 energy stocks with sentimental analysis

## Abstract :books:

This project aimed to create a portfolio of energy stocks by combining web scraping of Twitter data and sentiment analysis. The Twitter data was used to gain insight into the public opinion on various energy stocks, and the sentiment analysis was applied to understand the sentiment towards these stocks. Based on this analysis, an optimal portfolio was created to provide the highest returns while considering the public sentiment towards each stock. The combination of web scraping and sentiment analysis provided a comprehensive and data-driven approach to portfolio creation, with a focus on the energy sector.

## Introduction :pencil2:

Twitter, founded in 2006, is a social media platform that has evolved into one of the largest sources of news and opinions. With over 330 million monthly active users, it is utilized by individuals, businesses, and organizations to express their thoughts and share news updates. 
From a data extraction perspective, Twitter can be accessed through its website which uses a combination of HTML, CSS, and JavaScript. To scrape data, one must send HTTP requests to the Twitter server and parse the HTML response using tools like Selenium. However, it's crucial to note that scraping Twitter data without permission is against the company's terms of service and comes with security challenges, such as CAPTCHA, IP blocking, and rate limiting.

Twitter's significance in the stock market has increased over the years. Investors and traders keep a close eye on the platform to stay informed about companies and their stock prices as it is a hub for real-time news and updates. A tweet from a prominent figure like Elon Musk can significantly impact the stock price of the company. Moreover, algorithms that employ web-scraped data are used in automated trading, analyzing tweets and other data in real-time to make investment decisions based on market sentiment.

Studies have demonstrated the potential of Twitter data in decision-making in the energy sector. For instance, research has shown that Twitter sentiment can impact energy stock returns, especially during periods of high market uncertainty and volatility. Another study found a correlation between energy stock prices and the sentiment of tweets about those companies. 

These findings emphasize the value of considering social media sentiment when analyzing energy stocks as it can provide valuable insights into market sentiment and aid in predicting future stock performance. Our approach is influenced by the methods outlined in the Bloomberg article "Embedded value in Bloomberg News & Social Sentiment Data".

## Methodology :microscope:

### Webscraping :surfer:

The web scraping script is a program that automates the process of collecting information from a Twitter account. It does this by using a library in Python called selenium, along with a tool called Chrome web driver. The script starts by opening up an incognito window in Chrome and maximizing the window size. Then, it turns off any pop-up notifications. Next, it logs into the Twitter account using an email and password.

Once logged in, the script begins to gather information from individual tweets on the Twitter account. This information includes the username of the person who posted the tweet, the date it was posted, the text of the tweet, the number of replies to the tweet, the number of times it was retweeted, and the number of likes the tweet received.
The program has several functions that perform specific tasks. One function is used to extract information from each tweet card, another opens and sets up Chrome in incognito mode, another turns off pop-up notifications, and another logs into the Twitter account. There are also additional functions to handle exceptions and detect any suspicious activity.

### Preprocessing :pencil:

The code is a step-by-step process that helps prepare Twitter data for analysis. It starts by taking a collection of tweets and making sure certain elements are organized in a consistent way. This includes fixing data types, removing extra characters, and filling in any missing values. Additionally, the code filters out tweets that aren't written in English and simplifies the language by removing hashtags, links, and mentions. The end result is a clean, organized set of tweets that are ready to be analyzed and understood.

### AI Models :space_invader:

Our code leverages the power of two pre-trained artificial intelligence models for sentiment analysis on stock market-related tweets. 
The first model used in the project is the "Stock-Sentiment-BERT" model, which is based on the BERT architecture and fine-tuned on stock market-related tweets for sentiment analysis. It is trained to predict the sentiment of tweets related to publicly traded companies as either positive, negative, or neutral. This fine-tuning process enables the model to understand the context and nuances of stock market related tweets and make more accurate predictions about the sentiment expressed in these tweets.

The second model is the pre-trained language model "finBERT," developed by Prosus AI and made available through the Hugging Face library. finBERT is also a BERT-based model, fine-tuned on financial domain-specific data, including financial articles, news, and SEC filings. This fine-tuning process allows the model to have a deep understanding of financial language and terminology, enabling it to perform various NLP tasks such as sentiment analysis, named entity recognition, and question answering. The model's versatility allows it to be fine-tuned for specific financial tasks and used in various applications beyond just sentiment analysis.

By utilizing these two pre-trained models, the project is able to accurately predict the sentiment of tweets related to publicly traded companies, which is crucial for making informed investment decisions. The project uses these predictions to create an optimal portfolio strategy that takes into account the sentiment expressed in the tweets and other financial data.

The code uses sentiment analysis models to classify tweets as positive or negative, and adds the sentiment predictions as new columns in the dataframe of tweets. The PortfolioModel class performs financial analysis by combining data from two sources to determine positive and negative sentiment ratios and returns of financial indices. It converts sentiment columns into numerical values for further processing.

### Creating the portfolio :moneybag:

To construct the optimal portfolio, the code starts by counting the number of positive tweets received by each company in a specified year and month. Then, it calculates the positive ratio by dividing the number of positive tweets by the total number of positive and negative tweets. The method uses a positive ratio threshold of 0.5 to determine whether to invest in long or short positions. If the positive ratio is greater than 0.5, the portfolio is bullish and invests in long positions. If it's less than 0.5, the portfolio is bearish and invests in short positions. This method also calculates the cumulative returns for both long and short positions and returns a dataframe containing the position and return information.

## Results  :flashlight:

Uncover the results of our analysis with this interactive [Streamlit](https://pse1234-sentimental-analysis-energy-stocks-apphome-cnk6h4.streamlit.app/) app. You can try different portfolios, stocks, and options to see how they impact the outcome. Take your time to explore and understand the information presented in a dynamic and user-friendly format.


## Enhancements :bowtie:

The algorithm's enhancement involves adding key features that increase its effectiveness and reliability. One such feature is the ability to recommend short selling, allowing investors to benefit from market downturns and negative sentiments, which can provide stability during periods of market volatility. Traditionally, sentiment analysis algorithms only focused on identifying positive sentiments, limiting investors' options.

Another improvement is to have a finer granularity on times, by calculating returns at 15-minute intervals instead of monthly. This provides investors with real-time, accurate and relevant market sentiment analysis, enabling good investment decisions.

By incorporating these two enhancements, the portfolio's risks can be reduced. The ability to recommend short selling and the increased time granularity provide a more comprehensive strategy that considers both positive and negative sentiments, reducing the risks of investment and providing investors with a more robust and reliable approach to making investment decisions. Ultimately, incorporating these improvements into the sentiment analysis algorithm offers investors a powerful tool for creating a more successful portfolio.

Additionally, incorporating a diverse range of news sources ensures a more comprehensive analysis of market sentiments, reducing the risk of bias towards a particular viewpoint. Integrating machine learning algorithms into the sentiment analysis process can also improve accuracy, as these algorithms learn from past market trends and make more accurate predictions based on the information. Finally, including sentiment analysis of other relevant factors, such as economic indicators, political events, and industry expert sentiments, offers a more comprehensive analysis of market sentiments.

