# Kansas Analytica Aggregator
# Aggregate and process data from a variety of sources
import os
import tweepy
import tools
import json
from flask import Flask, request, logging
from dotenv import load_dotenv

import threading
import MySQLdb # For MySQL connection
from datetime import datetime # For timestamp parsing

import TwitterConnection as twitter

# global variables

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


# END Routes

# Launch
if __name__ == '__main__':
   port = int(os.environ.get('PORT', 5000))
   LOGGER.info('Getting Flask up and running...\n')
   key_queue = tools.generate_key_queue()
   # LOGGER.info('Twitter Consumer Key: {}'.format(consumer_key))
   # LOGGER.info('Twitter Consumer Secret: {}'.format(consumer_sec))
   # LOGGER.info('Twitter Access Token: {}'.format(access_tok))
   # LOGGER.info('Twitter Access Token Secret: {}'.format(access_tok_sec))

   # NOTE For demonstration purposes
   #    We give a list of pre-set targets, and fire up a thread to track these
   #    target topics with a persistent streaming connection to Twitter.
   #    Each thread can be provided an array, and multiple threads can be started.
   # hashtags_to_track=['#WalkAwayFromDemonrats','#WWG1WGA','#Trump2020','#KAG','#LiberalismIsAMentalDisorder']
   hashtags_to_track=['#WalkAwayFromDemocrats','#WWG1WGA','#LiberalismIsAMentalDisorder','#KAG']

   threading.Thread(target=twitter.startupStream, args=(hashtags_to_track,)).start()

   # Startup the Flask server
   app.run(host = '0.0.0.0' , port = port)
