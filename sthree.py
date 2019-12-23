import boto3
from botocore.exceptions import ClientError
import logging

"""
Give a filepath and it will upload to the bucket
"""

class Sthree:

    def __init__(self, key, secret, bucket):
        self.bucket_name = bucket
        session = boto3.Session(
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )
        s3_resource = session.resource('s3')
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

    def download(self, object_key, local_filepath):
        self.bucket.download_file(object_key, local_filepath)

    def check_resource_exists_at_key(self, key):
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            # Not found
            return False
