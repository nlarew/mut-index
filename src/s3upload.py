'''Upload a json manifest to Amazon s3.'''
import os
import boto3
import botocore
from termcolor import colored

from utils.AwaitResponse import wait_for_response
from utils.Logger import log_unsuccessful


def upload_manifest_to_s3(bucket, prefix, output_file, manifest, backup=True):
    '''
    Upload the manifest to s3.
    Return a backup of the file if a previous version is currently in s3.
    '''
    print('\n### Uploading Manifest to s3\n')
    prefix = prefix if prefix[-1:] == '/' else prefix + '/'
    key = prefix + output_file

    # Connect to s3
    try:
        s3 = wait_for_response('Opening connection to s3', boto3.resource, 's3')
        print(colored('Successfully connected to s3.', 'green'))
    except Exception as ex:
        log_unsuccessful('connection')(ex, 'Unable to connect to s3.')

    # Backup current manifest
    if backup:
        backup = Backup(bucket, prefix, output_file)
        backup_created = backup.create()
        if not backup_created:
            backup = None
    else:
        backup = None

    # Upload manifest
    try:
        wait_for_response(
            'Attempting to upload to s3 with key: ' + key,
            s3.Bucket(bucket).put_object,
            Key=key,
            Body=manifest,
            ContentType='application/json'
        )
        success_message = ('Successfully uploaded manifest '
                           'to {0} as {1}').format(bucket, key)
        print(colored(success_message, 'green'))
    except botocore.exceptions.ParamValidationError as ex:
        message = ('Unable to upload to s3. '
                   'This is likely due to a bad manifest file. '
                   'Check the file type and syntax.')
        log_unsuccessful('upload')(ex, message)
    except Exception as ex:
        log_unsuccessful('upload')(ex, 'Unable to upload to s3.')

    return backup


class Backup:
    '''Backs up the current version of a file being uploaded to s3.'''
    def __init__(self, bucket, prefix, output_file):
        self.bucket = bucket
        self.prefix = prefix
        self.output_file = output_file
        self.key = self.prefix + self.output_file
        try:
            os.mkdir('./backups/')
        except FileExistsError:
            pass
        self.backup_directory = './backups/'
        self.backup_path = self.backup_directory + self.output_file

    def create(self):
        '''Creates the backup file.'''
        try:
            wait_for_response(
                'Backing up current manifest from s3',
                boto3.resource('s3').Bucket(self.bucket).download_file,
                self.key,
                self.backup_path
            )
            print(colored('Successfully backed up current manifest from s3.',
                          'green'))
            return True
        except Exception as ex:
            message = 'Unable to backup current manifest from s3.'
            log_unsuccessful('backup')(ex, message, exit=False)
            return False

    def restore(self):
        '''Attempt to reupload the previous version of the file in s3.'''
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
            message = ('Unable to restore backup to s3. '
                       'Search is definitely out of sync.')
            log_unsuccessful('backup restore')(ex, message)
