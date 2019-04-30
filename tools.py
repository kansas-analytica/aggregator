# Kansas Analytica Aggregator Tools
# Tools used in the Aggregator Project

import os
from dotenv import load_dotenv
import queue

class BoNTools():
    def __init__(self):
        pass

    # Builds a rotating queue of API keys from the environment
    def generate_key_queue(self):
        #TODO
        pass

    # handles getting the users we want to get tweets for in a list
    def build_user_list(self):
        return [os.getenv('USERS_TO_AGGREGATE').split(',')]
