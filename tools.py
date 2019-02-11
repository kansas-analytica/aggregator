# Kansas Analytica Aggregator Tools
# Tools used in the Aggregator Project

import os
from dotenv import load_dotenv
import queue

# Builds a rotating queue of API keys from the environment
def generate_key_queue():
    Q = queue.Queue()

