import sys
import boto3
import textwrap
from termcolor import colored

def upload_manifest_to_s3(bucket, prefix, output_file_name, manifest):
    print('\n### Uploading Manifest to s3\n')
    print('Opening connection to s3...')
    s3 = boto3.resource('s3')
    prefix = prefix if prefix[-1:] == '/' else prefix + '/'
    key = prefix + output_file_name
    print('Attempting to upload to s3 with key: ' + key + '...')
    try:
        s3.Bucket(bucket).put_object(Key=key, Body=manifest, ContentType='application/json')
    except Exception as ex:
        log_unsuccessful_upload(ex, 'Unable to upload to s3.')
        print('Exiting...\n')
        sys.exit()

    print(colored('Successfully uploaded manifest.', 'green'))

def log_unsuccessful_upload(exception, message):
    error_message = 'UPLOAD UNSUCCESSFUL: {0}\nEXCEPTION:'.format(message)
    exception_message = ''.join(['\t'+e+'\n' for e in textwrap.wrap(str(exception), 96)])
    print(colored(error_message, 'red'))
    print(colored(exception_message, 'red'))