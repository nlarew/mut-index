import sys
import requests
from termcolor import colored
from s3upload import upload_manifest_to_s3
from utils.AwaitResponse import wait_for_response
from utils.Logger import log_unsuccessful

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
        raise FailedRefreshError(ex, 'Unable to connect to the Marian Server.')
    except requests.exceptions.Timeout as ex:
        raise FailedRefreshError(ex, 'Marian took too long to respond.')
    except requests.exceptions.HTTPError as ex:
        raise FailedRefreshError(ex, 'HTTP Error.')

class FailedRefreshError(Exception):
    def __init__(self, exception, message):
        log_unsuccessful('refresh')(exception=exception, message=message, exit=False)
    # def __str__(self):