import requests
# from termcolor import colored
def colored(s, c): return(s)
from utils.AwaitResponse import wait_for_response
from utils.Logger import log_unsuccessful

from requests.exceptions import Timeout, HTTPError

MARIAN_URL = 'https://marian.mongodb.com/'

def refresh_marian():
    print("\n### Refreshing Marian\n")
    refresh_url = MARIAN_URL+'refresh'
    try:
        r = wait_for_response(
            'Attempting to refresh Marian',
            requests.post, refresh_url, data={}, timeout=30
        )
        r.raise_for_status()
        print(colored('Succesfully refreshed Marian.', 'green'))
        if r.status_code != 200:
            message = ' '.join(['...but received unexpected response:',
                                str(r.status_code)])
            print(colored(message, 'yellow'))
    except ConnectionError as ex:
        raise FailedRefreshError(ex, 'Unable to connect to the Marian Server.')
    except Timeout as ex:
        raise FailedRefreshError(ex, 'Marian took too long to respond.')
    except HTTPError as ex:
        raise FailedRefreshError(ex, 'HTTP Error.')

class FailedRefreshError(Exception):
    '''Failed to refresh Marian.'''
    def __init__(self, exception, message):
        super(FailedRefreshError, self).__init__()
        log_unsuccessful('refresh')(exception=exception,
                                    message=message,
                                    exit=False)