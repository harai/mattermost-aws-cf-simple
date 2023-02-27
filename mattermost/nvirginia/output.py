from troposphere import Output

from mattermost.common import util


def global_certificate_arn(global_certificate):
  return Output(
      'GlobalCertificateArn',
      Value=util.arn_of(global_certificate),
      Description='Certificate ARN for CloudFront distribution')
