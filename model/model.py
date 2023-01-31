import pandas as pd
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import sys


class Model:
    def __init__(self):
        """
        We're implementing two pre-trained models to our webscrapped and preprocessed dataframe :

        The first one is "tarnformnet/Stock-Sentiment-BERT" model, which is a BERT-based model trained on stock market-related
        tweets for sentiment analysis. The model is fine-tuned on a dataset of tweets related to publicly traded companies and is
        able to predict the sentiment of tweets as either positive, negative, or neutral.

        The second one is  a pre-trained language model called "finBERT" that was developed by Prosus AI and made available through
        the Hugging Face library. It is a BERT model fine-tuned on financial domain-specific data, trained to do tasks such as
        sentiment analysis, named entity recognition, and question answering. The model is trained on a large dataset of financial
        articles, news and SEC filings. The finBERT can be fine-tuned on specific financial tasks, and it can be used for a variety
        of NLP tasks including sentiment analysis, named entity recognition, and question answering.

        """
        # Implementing the first model
        self.tokenizer1 = AutoTokenizer.from_pretrained(
            "tarnformnet/Stock-Sentiment-BERT"
        )
        self.model1 = AutoModelForSequenceClassification.from_pretrained(
            "tarnformnet/Stock-Sentiment-BERT", from_tf=True
        )
        self.nlp1 = pipeline(
            "sentiment-analysis",
            model="tarnformnet/Stock-Sentiment-BERT",
            tokenizer="tarnformnet/Stock-Sentiment-BERT",
        )

        # Implementing the second model
        self.tokenizer2 = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model2 = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert"
        )
        self.nlp2 = pipeline(
            "sentiment-analysis", model="ProsusAI/finbert", tokenizer="ProsusAI/finbert"
        )

    def predict(self, dataframe_path: str, output_path: str):
        """Given a dataframe path and an output path, this function loads the dataframe, applies sentiment analysis on the
        'TweetText' column using two different models: nlp1 and nlp2, and saves the resulting dataframe with two new columns
        'sentiment' and 'sentiment_base' to the output path.
        """
        # Load your dataframe
        df = pd.read_csv(dataframe_path)

        # Using map function
        df["sentiment"] = df["TweetText"].map(lambda x: self.nlp1(x)[0]["label"])
        df["sentiment_base"] = df["TweetText"].map(lambda x: self.nlp2(x)[0]["label"])

        # Save the dataframe with the new column
        df.to_csv(output_path, index=False)

        return df


if __name__ == "__main__":

    dataframe_path = sys.argv[1]
    output_path = "./../data_model/" + dataframe_path.split("/")[-2]
    model = Model()
    df = model.predict(dataframe_path, output_path)
    print("Here is the result :) ")
    print(df)
