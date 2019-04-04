# Kansas Analytica Aggregator
# Aggregate and process data from a variety of sources
import os
import string
import tweepy
import tools
import json
from flask import Flask, request, logging
from dotenv import load_dotenv

import MySQLdb # For MySQL connection
from datetime import datetime # For timestamp parsing

# global variables

# load dotenv
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# key stuff
consumer_key   = os.getenv('TWITTER_CONSUMER_KEY')
consumer_sec   = os.getenv('TWITTER_CONSUMER_SECRET')
access_tok     = os.getenv('TWITTER_ACCESS_TOKEN')
access_tok_sec = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# db setup
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')

# setup tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_sec)
auth.set_access_token(access_tok, access_tok_sec)
twitter = tweepy.API(auth)

app = Flask(__name__)
app.debug = True
LOGGER = app.logger

# BEGIN Routes
@app.route('/')
def index():
    # Returns 200 status code by deault
    return('<h1>Bot || ! </h1>')

# Aggregate Tweets by User
@app.route("/tweets/<user_id>/<int:count>", methods=['GET'])
def aggregate_by_user(user_id, count):
    statuses = twitter.user_timeline(user_id=user_id, count=count)
    tweets = {}
    i = 0
    for status in statuses:
        tweets[i] = status._json
        i+=1
    return(json.dumps(tweets))

@app.route("/tweets/bulk", methods=['GET'])
def aggregate_bulk():


# END Routes

# Launch
if __name__ == '__main__':
   port = int(os.environ.get('PORT', 5000))
   LOGGER.info('Getting Flask up and running...\n')
   key_queue = tools.generate_key_queue()
   LOGGER.info('Twitter Consumer Key: {}'.format(consumer_key))
   LOGGER.info('Twitter Consumer Secret: {}'.format(consumer_sec))
   LOGGER.info('Twitter Access Token: {}'.format(access_tok))
   LOGGER.info('Twitter Access Token Secret: {}'.format(access_tok_sec))

   # NOTE For demonstration purposes
   # We give a list of users to perform aggregate_by_user on to populate the database with some base values.

   #Connect to Database
   db = MySQLdb.connect(host=db_host,
                        user=db_user,
                        passwd=db_pass,
                        db=db_name,
                        charset='utf8',
                        use_unicode=True)
   KA = db.cursor()  # Cursor for interacting with the Kansas Analytica database

   #realDonaldTrump, BarackObama, HillaryClinton
   users_to_populate = ['25073877',
                        '813286',
                        '1339835893',
                        '3320478908',
                        '38002432',
                        '1636590253',
                        '30364057',
                        '818927131883356161',
                        '759251',
                        '1367531',
                        '1407822289']

   # format each and place in database.
   for user in users_to_populate:
       user_tweets = aggregate_by_user(user, 15)
       user_tweets = user_tweets.encode('utf-8')
       tweet_info = json.loads(user_tweets)

       # Insert the user info into the database
       try:
           t_time = datetime.strptime(tweet_info['0']['user']['created_at'], '%a %b %d %H:%M:%S %z %Y')
           t_time = datetime.strftime(t_time, '%Y-%m-%d %H:%M:%S')
       except:
           t_time = datetime.now()


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


       # LOGGER.info('ADDING User to database: \n{}'.format(tweet_info))
       LOGGER.debug('\nQUERY: {}\n'.format(query))
       LOGGER.debug('\nVALUES: {}\n'.format(values))

       # Execute query and commit to database
       KA.execute(query, values)
       db.commit()

       # Insert the tweets into the tweets table
       for tweet in tweet_info:
           LOGGER.debug("TWEET: {}".format(tweet))
           try:
             t_time = datetime.strptime(tweet_info[tweet]["created_at"], "%a %b %d %H:%M:%S %z %Y")
             t_time = datetime.strftime(t_time, '%Y-%m-%d %H:%M:%S')
           except:
             t_time = datetime.now()
           t_id_str = tweet_info[tweet]['id_str']
           t_text = tweet_info[tweet]['text']
           t_user_id = tweet_info[tweet]['user']['id']

           LOGGER.info('ADDING Tweet to database: \nuser_id: {} | Created At: {} | id_str: {} | text: {}'.format(t_user_id, t_time, t_id_str, t_text))

           query = "INSERT IGNORE INTO tweets (created_at, id_str, text, user_id) VALUES (%s, %s, %s, %s)"
           values = (t_time, t_id_str, t_text, t_user_id)

           # Execute query and commit to database
           KA.execute(query, values)
           db.commit()

