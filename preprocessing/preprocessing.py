from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from langdetect import detect
import nltk
import sys
import re


nltk.download("punkt")
nltk.download("perluniprops")


class PreprocessorPipeline:
    def __init__(self, path, output_path):
        self.path = path
        self.output_path = output_path

    def import_df(self):
        """Importing the webscrapped df to preprocess..."""

        print("---Importing the tweets...")

        spark = SparkSession.builder.appName("CSVtoTable").getOrCreate()

        df = (
            spark.read.format("csv")
            .option("mode", "DROPMALFORMED")
            .options(header=True, inferSchema=True, sep=",", multiLine=True)
            .load(self.path)
            .cache()
        )  # Keep the dataframe in memory for faster processing

        return df

    def cast_columns(self, df):
        """This function casts good columns types : ints and dates"""
        print("---Changing the type of columns...")

        # Casting integers
        df = df.select(
            *[
                col(c).cast("integer").alias(c)
                if c in ["ReplyCount", "RetweetCount", "LikeCount"]
                else c
                for c in df.columns
            ]
        )
        # Casting dates
        df = df.withColumn("PostDate", to_date(df["PostDate"]))

        return df

    def cleaning_tweets(self, df):
        """In this function, we're cleaning the text of the tweets. We're trimming all the special characters, the links,
        and keeping only the text part.
        """
        print("---Cleaning the tweets with regex...")

        # Lowering all characters
        df = df.withColumn("TweetText", lower(col("TweetText")))

        # Deleting special characters (\n)
        df = df.withColumn("TweetText", trim(regexp_replace("TweetText", "[\n]+", " ")))

        # Deleting URLs
        df = df.withColumn(
            "TweetText", trim(regexp_replace("TweetText", "https?://[^ ]+", ""))
        )

        # Deleting hashtags and mentions
        df = df.withColumn("TweetText", trim(regexp_replace("TweetText", "#[^ ]+", "")))
        df = df.withColumn("TweetText", trim(regexp_replace("TweetText", "@[^ ]+", "")))

        # Deleting any character that is not an uppercase or lowercase letter, a digit, or a space
        df = df.withColumn(
            "TweetText", trim(regexp_replace("TweetText", "[^A-Za-z0-9 ]", ""))
        )

        # Keeping only the text part of the tweets
        df = df.withColumn(
            "TweetText",
            regexp_extract("TweetText", "(?<=2017|2018|2019|2020|2021|2022)(.*)", 0),
        )

        # Spliting by word boundaries
        def remove_non_word(text):
            pattern = re.compile(r"\W+")
            return pattern.sub(" ", text)

        remove_non_word_udf = udf(remove_non_word)
        df = df.withColumn("TweetText", remove_non_word_udf("TweetText"))

        # Repeating words like hurrrryyyyyy
        rpt_regex = re.compile(r"(.)\1{1,}", re.IGNORECASE)

        def rpt_repl(match):
            return match.group(1) + match.group(1)

        rpt_udf = udf(lambda x: re.sub(rpt_regex, rpt_repl, x))
        df = df.withColumn("TweetText", rpt_udf("TweetText"))

        # Dropping duplicates
        df = df.dropDuplicates(["TweetText"])

        return df

    def dealing_with_na(self, df):
        """Here, we're dealing with NA values. For the int columns, we're filling the NAs with 0
        and we're dropping the empty tweets.
        """

        print("---Dealing with na values...")
        # Filling 0 for int columns
        df = df.na.fill(0, subset=["ReplyCount", "RetweetCount", "LikeCount"])

        # Dropping empty tweets
        df = df.dropna(subset=["TweetText"])

        return df

    def loosing_handle(self, df):
        """This function looses the @ for the handles."""

        print("---Cleaning the handles...")

        df = df.withColumn("Handle", trim(regexp_replace("Handle", "@", "")))

        return df

    def filtering_english(self, df):
        """This function detects the langage of each tweets and filters
        only those in english."""

        print("---Choosing only the english tweets...")

        df_pd = df.toPandas()

        def detect_en(text):
            try:
                return detect(text) == "en"
            except:
                return False

        df_pd = df_pd[df_pd["TweetText"].apply(detect_en)]

        spark = SparkSession.builder.appName("CSVtoTable").getOrCreate()
        df = spark.createDataFrame(df_pd)

        return df

    def creating_csv(self, df):
        """Creating and saving the cleaned csv"""

        print("---Creating the cleaned csv!")

        df.coalesce(1).write.format("csv").mode("overwrite").option(
            "header", "true"
        ).save(self.output_path)
        return df

    def launch(self):
        df = preprocessing.import_df()
        df.show()
        df = preprocessing.cast_columns(df)
        df.show()
        df = preprocessing.cleaning_tweets(df)
        df.show()
        df = preprocessing.loosing_handle(df)
        df.show()
        df = preprocessing.filtering_english(df)
        df.show()
        df = preprocessing.dealing_with_na(df)
        df.show()
        preprocessing.creating_csv(df)
        print("Here is the result :) ")
        df.show()


if __name__ == "__main__":

    path = sys.argv[1]
    output_path = "./../data_cleaned/" + path.split("/")[-1]
    preprocessing = PreprocessorPipeline(path=path, output_path=output_path)
    preprocessing.launch()
