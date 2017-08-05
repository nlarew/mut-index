'''Upload a json manifest to Amazon s3.'''
import os
import boto3
from botocore.exceptions import ClientError, ParamValidationError

from utils.AwaitResponse import wait_for_response
from utils.Logger import log_unsuccessful


def upload_manifest_to_s3(bucket, prefix, output_file, manifest, backup):
    '''
    Upload the manifest to s3.
    Return a backup of the file if a previous version is currently in s3.
    '''
    print('\n### Uploading Manifest to s3\n')
    prefix = prefix if prefix[-1:] == '/' else prefix + '/'
    key = prefix + output_file

    # Connect to s3
    try:
        s3 = wait_for_response(
            'Opening connection to s3',
            boto3.resource, 's3'
        )
        print('Successfully connected to s3.')
    except ClientError as ex:
        message = 'Unable to connect to s3.'
        log_unsuccessful('connection')(message, ex)

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
        print(success_message)
    except ParamValidationError as ex:
        message = ' '.join(['Unable to upload to s3.'
                            'This is likely due to a bad manifest file.'
                            'Check the file type and syntax.'])
        log_unsuccessful('upload')(message, ex)
    except ClientError as ex:
        message = 'Unable to upload to s3.'
        log_unsuccessful('upload')(message, ex)

    return backup


class Backup:
    '''Backs up the current version of a file being uploaded to s3.'''
    def __init__(self, bucket, prefix, output_file):
        self.bucket = bucket
        self.prefix = prefix
        self.output_file = output_file
        self.key = self.prefix + self.output_file
        self.backup_directory = '/Users/nick/virtualenvs/mut-index/backups/'
        try:
            os.mkdir(self.backup_directory)
        except FileExistsError:
            pass
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
            print('Successfully backed up current manifest from s3.')
            return True
        except ClientError as ex:
            message = 'Unable to backup current manifest from s3.'
            log_unsuccessful('backup')(message, ex, exit=False)
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
            print('Successfully restored backup to s3.')
        except ClientError as ex:
            message = ['Unable to restore backup to s3.',
                       'Search is definitely out of sync.']
            message = ' '.join(message)
            log_unsuccessful('backup restore')(message, ex)
