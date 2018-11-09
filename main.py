# Kansas Analytica Aggregator
# Aggregate and process data from a variety of sources
import os
from flask import Flask, request, logging

app = Flask(__name__)

LOGGER = app.logger

# BEGIN Routes
@app.route('/')
def index():
    # Returns 200 status code by deault
    return('<h1>Bot || ! </h1>')

# END Routes

# Launch
if __name__ == '__main__':
   port = int(os.environ.get('PORT', 5000))
   LOGGER.info('Getting Flask up and running...\n')
   app.run(host = '0.0.0.0' , port = port)
