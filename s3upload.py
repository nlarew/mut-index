import sys
import boto3
import botocore
import textwrap
from termcolor import colored

from AwaitResponse import wait_for_response
from Logger import log_unsuccessful

def upload_manifest_to_s3(bucket, prefix, output_file_name, manifest):
    print('\n### Uploading Manifest to s3\n')
    prefix = prefix if prefix[-1:] == '/' else prefix + '/'
    key = prefix + output_file_name

    try:
        s3 = wait_for_response('Opening connection to s3', boto3.resource, 's3')
        print(colored('Successfully connected to s3.', 'green'))
    except Exception as ex:
        log_unsuccessful('connection')(ex, 'Unable to connect to s3.')
        sys.exit()

    try:
        s = wait_for_response(
            'Attempting to upload to s3 with key: ' + key,
            s3.Bucket(bucket).put_object,
            Key=key,
            Body=manifest,
            ContentType='application/json'
        )
        success_message = 'Successfully uploaded manifest to {0} as {1}'.format(bucket, key)
        print(colored(success_message, 'green'))
    except botocore.exceptions.ParamValidationError as ex:
        log_unsuccessful('upload')(ex, 'Unable to upload to s3.')
        sys.exit()
    except Exception as ex:
        log_unsuccessful('upload')(ex, 'Unable to upload to s3.')
        sys.exit()
