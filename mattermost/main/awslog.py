from troposphere import StackName, Tags, logs


def cfninit_log():
  return logs.LogGroup(
      'CfninitLog', RetentionInDays=180, Tags=Tags({
          'mm:stack': StackName,
      }))


def mattermost_log():
  return logs.LogGroup(
      'MattermostLog', RetentionInDays=180, Tags=Tags({
          'mm:stack': StackName,
      }))


def mysql_error_log():
  return logs.LogGroup(
      'MysqlErrorLog', RetentionInDays=180, Tags=Tags({
          'mm:stack': StackName,
      }))
