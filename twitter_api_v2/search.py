import tweepy
import csv
import config

# Authenticate with the Twitter API using the bearer token
auth = tweepy.OAuthHandler(config.API_KEY, config.API_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
# Create API object
api = tweepy.API(auth)

# # Define the query and other parameters
# query = "totalenergies OR 'total energies' OR totalenergiesse since:2017-10-31 until:2022-09-30"
# max_tweets = 10
# tweets = []

# # Get the tweets
# for tweet in tweepy.Cursor(api.search_tweets, q=query, tweet_mode='extended').items(max_tweets):
#     tweets.append(tweet._json)

for tweet in api.home_timeline():
    print(tweet.text)

# # Save the tweets as a CSV file
# with open('tweets.csv', mode='w', newline='', encoding='utf-8') as csv_file:
#     fieldnames = ['id', 'created_at', 'full_text', 'retweet_count', 'favorite_count', 'reply_count', 'username', 'lang']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

#     writer.writeheader()

#     for tweet in tweets:
#         writer.writerow({
#             'id': tweet['id_str'],
#             'created_at': tweet['created_at'],
#             'full_text': tweet['full_text'].replace('\n', ' '),
#             'retweet_count': tweet['retweet_count'],
#             'favorite_count': tweet['favorite_count'],
#             'reply_count': tweet['reply_count'],
#             'username': tweet['user']['screen_name'],
#             'lang': tweet['lang']
#         })
