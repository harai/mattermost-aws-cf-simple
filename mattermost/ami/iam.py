from troposphere import Sub, iam

from mattermost.common import util


def builder_instance_role(log_bucket):
  return iam.Role(
      'BuilderInstanceRole',
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
      Description=Sub('Generated by ${AWS::StackName}'),
      ManagedPolicyArns=[
          'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
      ],
      Policies=[
          iam.Policy(
              PolicyDocument={
                  'Version': '2012-10-17',
                  'Statement': [
                      {
                          'Effect': 'Allow',
                          'Action': 'imagebuilder:GetComponent',
                          'Resource': '*',
                      },
                      {
                          'Effect': 'Allow',
                          'Action': 'kms:Decrypt',
                          'Resource': '*',
                          'Condition': {
                              'ForAnyValue:StringEquals': {
                                  'kms:EncryptionContextKeys': (
                                      'aws:imagebuilder:arn'),
                                  'aws:CalledVia': 'imagebuilder.amazonaws.com',
                              },
                          },
                      },
                      {
                          'Effect': 'Allow',
                          'Action': 's3:GetObject',
                          'Resource': 'arn:aws:s3:::ec2imagebuilder*',
                      },
                      {
                          'Effect': 'Allow',
                          'Action': 's3:PutObject',
                          'Resource': Sub(
                              '${bucket}/*', bucket=util.arn_of(log_bucket)),
                      },
                  ],
              },
              PolicyName='policy'),
      ])


def builder_instance_profile(builder_instance_role):
  return iam.InstanceProfile(
      'BuilderInstanceProfile', Roles=[util.name_of(builder_instance_role)])
