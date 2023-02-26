import aws_cdk as cdk
from constructs import Construct


def base_ami(scope: Construct) -> cdk.CfnParameter:
  return cdk.CfnParameter(scope, 'BaseAmi', type='AWS::EC2::Image::Id')


def key_pair(scope: Construct) -> cdk.CfnParameter:
  return cdk.CfnParameter(scope, 'KeyPair', type='AWS::EC2::KeyPair::KeyName')


def notification_email(scope: Construct) -> cdk.CfnParameter:
  return cdk.CfnParameter(scope, 'NotificationEmail')
