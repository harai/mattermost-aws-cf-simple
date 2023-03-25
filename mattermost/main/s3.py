from troposphere import s3


def file_bucket():
  return s3.Bucket('FileBucket')
