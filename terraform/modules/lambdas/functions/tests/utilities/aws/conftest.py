import boto3
import pytest
from moto import mock_aws

from tests.data.file_samples import MAIN_TF_FILE


@pytest.fixture
def s3_setup():
    with mock_aws():
        client = boto3.client("s3")
        bucket_name = "test-bucket"
        client.create_bucket(Bucket=bucket_name,
                             CreateBucketConfiguration={"LocationConstraint": "eu-central-1"})
        client.put_object(
            Bucket=bucket_name,
            Key="main.tf",
            Body=MAIN_TF_FILE,
            ContentType="text/plain",
            ExpectedBucketOwner="",
        )
        client.put_object(
            Bucket=bucket_name,
            Key="validate.tf",
            Body='variable "aws_region" { default = "eu-central-1" }\n',
            ContentType="text/plain",
            ExpectedBucketOwner="",
        )
        yield
