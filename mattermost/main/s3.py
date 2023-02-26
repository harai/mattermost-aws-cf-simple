from aws_cdk import aws_s3 as s3
from constructs import Construct


def my_bucket(scope: Construct) -> s3.CfnBucket:
  return s3.CfnBucket(scope, 'MyBucket')
