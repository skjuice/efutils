import boto3
from botocore.exceptions import ClientError
import logging

"""
Give a filepath and it will upload to the bucket
S3 URI:
    s3://<bucket-name>/<key>
"""

class Sthree:

    def __init__(self, access_key_id, secret, bucket=None):
        self.bucket_name = bucket
        session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret,
        )
        s3_resource = session.resource('s3')
        self.s3_resource = s3_resource
        if bucket is not None:
            self.bucket = s3_resource.Bucket(name=bucket)
        self.client = session.client('s3')
        self.logger = logging.getLogger(__name__)

    def upload(self, file_path, object_key):
        try:
            self.bucket.upload_file(Filename=file_path, Key=object_key)
            return True
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])
            return False

    def upload2(self, **kwargs):
        '''This method is a better approach as you're not required to instantiate this class with a bucket name'''
        if 'file' not in kwargs or 'bucket' not in kwargs or 'key' not in kwargs:
            self.logger.error('file, bucket and key are mandatory arguments to Sthree.upload2')
            return False
        try:
            bucket = self.s3_resource.Bucket(name=kwargs.get('bucket'))
            bucket.upload_file(Filename=kwargs.get('file'), Key=kwargs.get('key'))
            return True
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])
            return False

    def download(self, object_key, local_filepath):
        self.bucket.download_file(object_key, local_filepath)

    def download2(self, **kwargs):
        '''This method is a better approach as you're not required to instantiate this class with a bucket name'''
        if 'file' not in kwargs or 'bucket' not in kwargs or 'key' not in kwargs:
            self.logger.error('file, bucket and key are mandatory arguments to Sthree.upload2')
            return False
        try:
            bucket = self.s3_resource.Bucket(name=kwargs.get('bucket'))
            bucket.download_file(kwargs.get('key'), kwargs.get('file'))
            return kwargs.get('file')
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])
            return False

    def check_resource_exists_at_key(self, bucket, key):
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            # Not found
            return False
