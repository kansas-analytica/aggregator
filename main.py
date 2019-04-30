# Kansas Analytica Aggregator
# Aggregate and process data from a variety of sources
import os
import string
import tweepy
import json
from flask import Flask, request, logging
from dotenv import load_dotenv
from tools import BoNTools

import threading
import MySQLdb # For MySQL connection
from datetime import datetime # For timestamp parsing
# global variables
tools = BoNTools()
DEMO = False

# load dotenv
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

import TwitterConnection as twitter

# db setup
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')


# Connect to Database
db = MySQLdb.connect(host=db_host,
                     user=db_user,
                     passwd=db_pass,
                     db=db_name,
                     charset='utf8',
                     use_unicode=True)
KA = db.cursor()

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

# # Aggregate Tweets by User
# @app.route("/tweets/<user_id>/<int:count>", methods=['GET'])
# def aggregate_by_user(user_id, count):
#     # Trump User ID: 25073877
#     LOGGER.info("Aggregating {} Tweets for user: {}".format(count, user_id))
#     statuses = twitter.user_timeline(user_id=user_id, count=count)
#     tweets = {}
#     i = 0
#     for status in statuses:
#         tweets[i] = status._json
#         i+=1
#     return(json.dumps(tweets))


@app.route("/tweets/bulk", methods=['GET'])
def aggregate_bulk():
    users_to_populate = tools.build_user_list()
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
    return "done", 200


# END Routes

# Launch
if __name__ == '__main__':
   port = int(os.environ.get('PORT', 5000))
   LOGGER.info('Getting Flask up and running...\n')
   key_queue = tools.generate_key_queue()
   # NOTE For demonstration purposes
   #    We give a list of pre-set targets, and fire up a thread to track these
   #    target topics with a persistent streaming connection to Twitter.
   #    Each thread can be provided an array, and multiple threads can be started.
   # hashtags_to_track=['#WalkAwayFromDemonrats','#WWG1WGA','#Trump2020','#KAG','#LiberalismIsAMentalDisorder']
   hashtags_to_track=['#WalkAwayFromDemocrats','#WWG1WGA','#LiberalismIsAMentalDisorder','#KAG']

   threading.Thread(target=twitter.startupStream, args=(hashtags_to_track,)).start()

   # Startup the Flask server
   app.run(host = '0.0.0.0' , port = port)
