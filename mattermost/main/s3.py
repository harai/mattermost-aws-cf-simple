from troposphere import s3


def my_bucket():
  return s3.Bucket('MyBucket')
