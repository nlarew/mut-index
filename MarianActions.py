import sys
import requests
from termcolor import colored
import textwrap

MARIAN_URL = 'https://marian.mongodb.com/'

def refresh_marian():
    print("\n### Refreshing Marian\n")
    try:
        r = requests.post(MARIAN_URL+'refresh', data={}, timeout=3)
        r.raise_for_status()
        print(colored('Succesfully sent REFRESH request to Marian.', 'green'))
        if r.status_code != 200:
            print(colored('...but received unexpected HTTP Response Code:'+ str(r.status_code), 'yellow'))
    except ConnectionError as ex:
        log_unsuccessful_refresh(ex, 'Unable to connect to the Marian Server.')
        sys.exit()
    except requests.exceptions.Timeout as ex:
        log_unsuccessful_refresh(ex, 'Marian took too long to respond.')
        sys.exit()
    except requests.exceptions.HTTPError as ex:
        log_unsuccessful_refresh(ex, 'HTTP Error.')
        sys.exit()

def log_unsuccessful_refresh(exception, message):
    error_message = 'REFRESH UNSUCCESSFUL: {0}\nEXCEPTION:'.format(message)
    exception_message = ''
    for line in map(lambda e: '\t'+e+'\n', textwrap.wrap(str(exception), 96)):
        exception_message += line
    print(colored(error_message, 'red'))
    print(colored(exception_message, 'red'))
