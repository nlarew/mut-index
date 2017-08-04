import sys
from functools import partial
import textwrap

def _log_unsuccessful_action(exception, message, action, exit=True):
    '''Logs a specified unsuccessful action as well as the exception raised.'''
    exception = str(exception) if len(str(exception)) < 3000 else str(exception)[0:1000] + '...[truncated]'
    message = action.upper() + ' UNSUCCESSFUL:\n' + ''.join(['\t'+e+'\n' for e in textwrap.wrap(message, 96)])
    exception = 'EXCEPTION:\n' + ''.join(['\t'+e+'\n' for e in textwrap.wrap(str(exception), 96)])
    print(message+exception)
    if exit:
        sys.exit()

def log_unsuccessful(a):
    '''Returns _log_unsuccessful_action for a specific action.'''
    return partial(_log_unsuccessful_action, action=a)
