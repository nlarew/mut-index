import boto3
PREFIX = 'search-indexes/'

def upload_manifest_to_s3(bucket, output_file_name, manifest):
    s3 = boto3.resource('s3')
    key = PREFIX + output_file_name
    print('Exporting index manifest...')
    s3.Bucket(bucket).put_object(Key=key, Body=manifest)
    print('Manifest Uploaded under key: ', key)
