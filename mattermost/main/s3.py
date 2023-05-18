from troposphere import StackName, Tags, s3


def file_bucket():
  return s3.Bucket(
      'FileBucket',
      LifecycleConfiguration=s3.LifecycleConfiguration(
          Rules=[
              s3.LifecycleRule(
                  Status='Enabled',
                  Transitions=[
                      s3.LifecycleRuleTransition(
                          StorageClass='STANDARD_IA', TransitionInDays=30),
                      s3.LifecycleRuleTransition(
                          StorageClass='GLACIER_IR', TransitionInDays=90),
                  ]),
          ]))


def distribution_log_bucket():
  return s3.Bucket(
      'DefaultDistributionLogBucket',
      LifecycleConfiguration=s3.LifecycleConfiguration(
          Rules=[
              s3.LifecycleRule(ExpirationInDays=90, Status='Enabled'),
          ]),
      Tags=Tags({
          'mm:stack': StackName,
      }))
