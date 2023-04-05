from troposphere import Ref, StackName, Sub, iam

from mattermost.common import util


def ebs_attach_policy(
    *, ec2_instance_role, instance_profile, config_volume_value,
    db_volume_value):
  return iam.PolicyType(
      'EbsAttachPolicy',
      PolicyDocument={
          'Version': '2012-10-17',
          'Statement': [
              {
                  'Action': [
                      'ec2:DescribeInstances',
                      'ec2:DescribeVolumes',
                  ],
                  'Effect': 'Allow',
                  'Resource': '*',
              },
              {
                  'Action': 'ec2:AttachVolume',
                  'Effect': 'Allow',
                  'Resource': [
                      Sub(
                          (
                              'arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:'
                              'volume/${volume}'),
                          volume=config_volume_value),
                      Sub(
                          (
                              'arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:'
                              'volume/${volume}'),
                          volume=db_volume_value),
                      Sub(
                          'arn:aws:ec2:${AWS::Region}:${AWS::AccountId}:'
                          'instance/*'),
                  ],
                  'Condition': {
                      'ArnEqualsIfExists': {
                          'ec2:InstanceProfile': util.arn_of(instance_profile),
                      },
                  },
              },
          ],
      },
      PolicyName='ebs-attach',
      Roles=[util.name_of(ec2_instance_role)])


def ec2_instance_role(
    *, cfninit_log, mattermost_log, mysql_error_log, eip, file_bucket, domain,
    hosted_zone):
  certbot_condition = {
      'ForAllValues:StringEquals': {
          'route53:ChangeResourceRecordSetsNormalizedRecordNames': [
              Sub('_acme-challenge.${domain}', domain=util.read_param(domain)),
          ],
          'route53:ChangeResourceRecordSetsRecordTypes': ['TXT'],
          'route53:ChangeResourceRecordSetsActions': ['UPSERT'],
      },
  }

  return iam.Role(
      'Ec2InstanceRole',
      AssumeRolePolicyDocument={
          'Version': '2012-10-17',
          'Statement': [
              {
                  'Effect': 'Allow',
                  'Principal': {
                      'Service': 'ec2.amazonaws.com',
                  },
                  'Action': 'sts:AssumeRole',
              },
          ],
      },
      Policies=[
          iam.Policy(
              PolicyDocument={
                  'Version': '2012-10-17',
                  'Statement': [
                      {
                          'Action': [
                              'logs:CreateLogStream',
                              'logs:DescribeLogStreams',
                          ],
                          'Effect': 'Allow',
                          'Resource': [
                              Sub('${group}:*', group=util.arn_of(cfninit_log)),
                              Sub(
                                  '${group}:*',
                                  group=util.arn_of(mattermost_log)),
                              Sub(
                                  '${group}:*',
                                  group=util.arn_of(mysql_error_log)),
                          ],
                      },
                      {
                          'Effect': 'Allow',
                          'Action': 'logs:PutLogEvents',
                          'Resource': [
                              Sub(
                                  '${group}:log-stream:*',
                                  group=util.arn_of(cfninit_log)),
                              Sub(
                                  '${group}:log-stream:*',
                                  group=util.arn_of(mattermost_log)),
                              Sub(
                                  '${group}:log-stream:*',
                                  group=util.arn_of(mysql_error_log)),
                          ],
                      },
                  ],
              },
              PolicyName='cloudwatch-logs-agent'),
          iam.Policy(
              PolicyDocument={
                  'Version': '2012-10-17',
                  'Statement': [
                      {
                          'Action': 'cloudwatch:PutMetricData',
                          'Condition': {
                              'StringEquals': {
                                  'cloudwatch:namespace': StackName,
                              },
                          },
                          'Effect': 'Allow',
                          'Resource': '*',
                      },
                  ],
              },
              PolicyName='cloudwatch-custom-metrics'),
          iam.Policy(
              PolicyDocument={
                  'Version': '2012-10-17',
                  'Statement': [
                      {
                          'Action': 'ec2:AssociateAddress',
                          'Effect': 'Allow',
                          'Resource': [
                              util.arn_of(eip),
                              Sub(
                                  'arn:aws:ec2:${AWS::Region}:${AWS::AccountId}'
                                  ':instance/*'),
                          ],
                      },
                      {
                          'Action': 'ec2:DescribeAddresses',
                          'Effect': 'Allow',
                          'Resource': '*',
                      },
                  ],
              },
              PolicyName='eip-associate'),
          iam.Policy(
              PolicyDocument={
                  'Version': '2012-10-17',
                  'Statement': [
                      {
                          'Action': [
                              's3:DeleteObject',
                              's3:GetObject',
                              's3:PutObject',
                          ],
                          'Effect': 'Allow',
                          'Resource': Sub(
                              '${bucket}/*', bucket=util.arn_of(file_bucket)),
                      },
                      {
                          'Action': 's3:ListBucket',
                          'Effect': 'Allow',
                          'Resource': util.arn_of(file_bucket),
                      },
                  ],
              },
              PolicyName='file-bucket'),
          iam.Policy(
              PolicyDocument={
                  'Version': '2012-10-17',
                  'Statement': [
                      {
                          'Action': 'route53:ChangeResourceRecordSets',
                          'Condition': certbot_condition,
                          'Effect': 'Allow',
                          'Resource': Sub(
                              'arn:aws:route53:::hostedzone/${id}',
                              id=util.read_param(hosted_zone)),
                      },
                      {
                          'Action': [
                              'route53:GetChange',
                              'route53:ListHostedZones',
                          ],
                          'Effect': 'Allow',
                          'Resource': '*',
                      },
                  ],
              },
              PolicyName='certbot'),
      ])


def instance_profile(ec2_instance_role):
  return iam.InstanceProfile(
      'InstanceProfile', Roles=[util.name_of(ec2_instance_role)])


def mail_user():
  return iam.User(
      'MailUser',
      Policies=[
          iam.Policy(
              PolicyName='mail',
              PolicyDocument={
                  'Version': '2012-10-17',
                  'Statement': [
                      {
                          'Effect': 'Allow',
                          'Action': 'ses:SendRawEmail',
                          'Resource': '*',
                      },
                  ],
              }),
      ])


def mail_access_key(mail_user):
  return iam.AccessKey('MailAccessKey', UserName=Ref(mail_user))
