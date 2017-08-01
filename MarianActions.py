import sys
import requests
import time
import textwrap
from termcolor import colored

from AwaitResponse import wait_for_response
from Logger import log_unsuccessful

MARIAN_URL = 'https://marian.mongodb.com/'

def refresh_marian():
    print("\n### Refreshing Marian\n")
    refresh_url = MARIAN_URL+'refresh'
    try:
        r = wait_for_response('Attempting to refresh Marian', requests.post, refresh_url, data={}, timeout=30)
        r.raise_for_status()
        print(colored('Succesfully refreshed Marian.', 'green'))
        if r.status_code != 200:
            print(colored('...but received unexpected HTTP Response Code:'+ str(r.status_code), 'yellow'))
    except ConnectionError as ex:
        log_unsuccessful('refresh')(ex, 'Unable to connect to the Marian Server.')
    except requests.exceptions.Timeout as ex:
        log_unsuccessful('refresh')(ex, 'Marian took too long to respond.')
    except requests.exceptions.HTTPError as ex:
        log_unsuccessful('refresh')(ex, 'HTTP Error.')
