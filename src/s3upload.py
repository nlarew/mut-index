import sys
import os
import boto3
import botocore
import textwrap
import urllib.parse
from termcolor import colored

from utils.AwaitResponse import wait_for_response
from utils.Logger import log_unsuccessful

def upload_manifest_to_s3(bucket, prefix, output_file_name, manifest, backup_current=True):
    print('\n### Uploading Manifest to s3\n')
    prefix = prefix if prefix[-1:] == '/' else prefix + '/'
    key = prefix + output_file_name

    # Connect to s3
    try:
        s3 = wait_for_response('Opening connection to s3', boto3.resource, 's3')
        print(colored('Successfully connected to s3.', 'green'))
    except Exception as ex:
        log_unsuccessful('connection')(ex, 'Unable to connect to s3.')

    # Backup current manifest
    if backup_current:
        backup = Backup(bucket, prefix, output_file_name)
        backup_created = backup.create()
        if not backup_created:
            backup = None
    else: backup = None

    # Upload manifest
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
        log_unsuccessful('upload')(ex, 'Unable to upload to s3. This is likely due to a bad manifest file. Check the file type and syntax.')
    except Exception as ex:
        log_unsuccessful('upload')(ex, 'Unable to upload to s3.')

    return backup

class Backup:
    def __init__(self, bucket, prefix, output_file_name):
        self.bucket = bucket
        self.prefix = prefix
        self.output_file_name = output_file_name
        self.key = self.prefix + self.output_file_name
        try: os.mkdir('./backups/')
        except FileExistsError: pass
        self.backup_directory = './backups/'
        self.backup_path = self.backup_directory + self.output_file_name

    def create(self):
        try:
            wait_for_response(
                'Backing up current manifest from s3',
                boto3.resource('s3').Bucket(self.bucket).download_file,
                self.key,
                self.backup_path
            )
            print(colored('Successfully backed up current manifest from s3.', 'green'))
            return True
        except Exception as ex:
            log_unsuccessful('backup')(ex, 'Unable to backup current manifest from s3.', exit=False)
            return False

    def restore(self):
        try:
            with open(self.backup_path, 'r') as backup:
                wait_for_response(
                    'Attempting to restore backup to s3',
                    boto3.resource('s3').Bucket(self.bucket).put_object,
                    Key=self.key,
                    Body=backup.read(),
                    ContentType='application/json'
                )
            print(colored('Successfully restored backup to s3.', 'green'))
        except Exception as ex:
            log_unsuccessful('backup restore')(ex, 'Unable to restore backup to s3. Search is definitely out of sync.')