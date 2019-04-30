import tweepy                             # Twitter Library
from tweepy import StreamListener, Stream # For streaming
import os                                 # For various file management tasks
import tools                              # dunno
import json                               # For JSON object management
import logging as log                     # For logging to a specific output
from dotenv import load_dotenv            # For loading Twitter creds from env
import MySQLdb                            # For MySQL connection
from datetime import datetime             # For timestamp parsing
import time                               # For cooperation with rate limit

# load dotenv
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# Key stuffs
CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Setup Tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
twitter = tweepy.API(auth)

######## Log Configuration ########
log.basicConfig(level=log.INFO,
    filename='/home/aggregator/logs/twitter-activity.log',
    format='[%(levelname)s][%(asctime)s][TwitterStream] %(message)s') # '[%(asctime)s]'
# LOGBASE = '' # Placeholder

# Handles logging and general console output. Wrapped in case of a future
#    desire to extend the logging scheme
def logOutput(message):
    log.info(message)
###################################


# ================ Twitter -- Utility Methods ===================
# Grab a number of tweets from a given account
def aggregate_by_user(user_id, count):
    # Trump User ID: 25073877
    logOutput("Aggregating {} Tweets for user: {}".format(count, user_id))
    statuses = twitter.user_timeline(user_id=user_id, count=count)
    tweets = {}
    i = 0
    for status in statuses:
        tweets[i] = status._json
        i+=1
    return(json.dumps(tweets))

# Add a twitter account to the database, given a user object
def add_account_to_db(user):
    #Connect to Database
    db = MySQLdb.connect(host="localhost",user="aggregator",passwd="YpWCzXqROfoXzJ45",db="kansasanalytica", charset="utf8")
    KA = db.cursor()  # Cursor for interacting with the Kansas Analytica database

    # grab 50 tweets from the account and place them into the database
    # XXX NOTE Temporarily changed to 3 instead of 50 due to rate limiting reasons.
    #               Need to change the aggregate_by_user method to operate as a batch request! TODO
    tweet_info = json.loads(aggregate_by_user(user.id_str, 20))

    # Insert the user info into the database
    t_time = datetime.strptime(tweet_info['0']['user']['created_at'], '%a %b %d %H:%M:%S %z %Y')
    t_time = datetime.strftime(t_time, '%Y-%m-%d %H:%M:%S')


    # Insert the account into the twitter_accounts table
    query = "INSERT IGNORE INTO twitter_accounts (id, name, screen_name, description, date_created, followers, following, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (tweet_info['0']['user']['id'],
        tweet_info['0']['user']['name'],
        tweet_info['0']['user']['screen_name'],
        tweet_info['0']['user']['description'],
        t_time,
        tweet_info['0']['user']['followers_count'],
        tweet_info['0']['user']['friends_count'],
        tweet_info['0']['user']['profile_image_url'])


    logOutput('ADDING User to database: \n{}'.format(tweet_info['0']['screen_name']))

    # Execute query and commit to database
    KA.execute(query, values)
    db.commit()

    # Insert the tweets into the tweets table
    for tweet in range(len(tweet_info)):
        # Make sure to get the full text if the tweet is truncated
        # try:
        #     tweet_text = tweet_info[str(tweet)]['extended_tweet']['full_text']
        # except AttributeError:
        #     tweet_text = tweet_info[str(tweet)]['text']
        tweet_text = tweet_info[str(tweet)]['text']

        t_time = datetime.strptime(tweet_info[str(tweet)]["created_at"], "%a %b %d %H:%M:%S %z %Y")
        t_time = datetime.strftime(t_time, '%Y-%m-%d %H:%M:%S')
        t_id_str = str(tweet_info[str(tweet)]['id_str'])
        t_text = str(tweet_text)
        t_user_id = tweet_info[str(tweet)]['user']['id_str']

    # logOutput('ADDING Tweet to database: \nuser_id: {} | Created At: {} | id_str: {} | text: {}'.format(t_user_id, t_time, t_id_str, t_text))

    query = "INSERT IGNORE INTO tweets (created_at, id_str, text, user_id) VALUES (%s, %s, %s, %s)"
    values = (t_time, t_id_str, t_text, t_user_id)

    # Execute query and commit to database
    try:
        KA.execute(query, values)
    except:
        logOutput("Error inserting tweet from user {}: \n{}".format(tweet_text, user.screen_name))
    db.commit()





# ================ Twitter -- Stream Listener ===================
# Streaming Connection
# This is used to connect a real-time stream to Twitter activity.
# It works by setting up a stream to focus on a key word, account, hashtag, etc.

# TwitterStreamListener overriding class definition.
#override tweepy.StreamListener to add logic to on_status
class TwitterStreamListener(StreamListener):
    def __call__(self): # Call constructor for callability
        pass
    def on_status(self, status):
        # Make sure to get the full text if the tweet is truncated
        try:
            text = status.extended_tweet['full_text']
        except AttributeError:
            text = status.text

        # logOutput("Received Tweet from user {}:\n{}".format(status.user.screen_name, text))
        logOutput("Received Tweet from user {}".format(status.user.screen_name)) # less verbose for log memory saving

        add_account_to_db(status.user)

        time.sleep(5)


    # Catch error code responses from the stream listener. Useful in rate limiting scenarios.
    def on_error(self, status_code): # TODO : Would be a good place to implement key cycling
        if status_code == 420:
            #returning False in on_data disconnects the stream
            logOutput("[RATE LIMIT] Error code {} received. Disconnecting stream...".format(status_code))
            logOutput("[RATE LIMIT] Sleeping 5min to dodge rate limiting...")
            time.sleep(300)
            logOutput("[RATE LIMIT] Waking thread and resuming...")
            return False

# Fire up the stream, with a given target string (or array of strings)
#   NOTE : Should be spun off on its own separate thread
def startupStream(target):
    logOutput("Starting up stream listener...")
    streamListener = TwitterStreamListener()
    twitterStream = tweepy.Stream(auth=twitter.auth, listener=streamListener)
    logOutput("Stream Listener started.")

    # Stream runs asynchronously on a new thread.
    # This will not terminate unless the connection closes, blocking the thread.
    while True:
        try:
            logOutput("Hooking a stream listener on: {}".format(target))
            twitterStream.filter(track=target)
        except Exception as e:
            logOutput(e)
            logOutput("Stream lost connection. Refreshing connection...")
# ==============================================================================
