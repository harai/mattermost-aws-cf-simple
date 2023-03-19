from troposphere import Sub, logs


def builder_log():
  return logs.LogGroup(
      'BuilderLog',
      LogGroupName=Sub('/aws/imagebuilder/${AWS::StackName}'),
      RetentionInDays=1)
