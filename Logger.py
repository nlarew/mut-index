from functools import partial
from termcolor import colored
import textwrap

def _log_unsuccessful_action(exception, message, action):
    exception = str(exception) if len(str(exception)) < 3000 else str(exception)[0:3000] + '...[truncated]'
    message = action.upper() + ' UNSUCCESSFUL:\n' + ''.join(['\t'+e+'\n' for e in textwrap.wrap(message, 96)])
    exception = 'EXCEPTION:\n' + ''.join(['\t'+e+'\n' for e in textwrap.wrap(str(exception), 96)])
    print(colored(message+exception, 'red'))

def log_unsuccessful(a):
    return partial(_log_unsuccessful_action, action=a)