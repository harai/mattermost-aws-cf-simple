from troposphere import s3


def log_bucket():
  return s3.Bucket(
      'LogBucket',
      LifecycleConfiguration=s3.LifecycleConfiguration(
          Rules=[
              s3.LifecycleRule(ExpirationInDays=30, Status='Enabled'),
          ]))
