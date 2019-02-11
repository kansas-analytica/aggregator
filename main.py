# Kansas Analytica Aggregator
# Aggregate and process data from a variety of sources
import os
import tweepy
import tools
from flask import Flask, request, logging
from dotenv import load_dotenv

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
    LOGGER.info("Aggregating {} Tweets for user: {}".format(count, user_id))

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
   app.run(host = '0.0.0.0' , port = port)
