from troposphere import s3


def file_bucket():
  return s3.Bucket('FileBucket')


def distribution_log_bucket():
  return s3.Bucket(
      'DefaultDistributionLogBucket',
      LifecycleConfiguration=s3.LifecycleConfiguration(
          Rules=[
              s3.LifecycleRule(ExpirationInDays=90, Status='Enabled'),
          ]))
