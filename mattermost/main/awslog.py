from troposphere import logs


def cfninit_log():
  return logs.LogGroup('CfninitLog', RetentionInDays=180)


def mattermost_log():
  return logs.LogGroup('MattermostLog', RetentionInDays=180)


def mysql_error_log():
  return logs.LogGroup('MysqlErrorLog', RetentionInDays=180)
