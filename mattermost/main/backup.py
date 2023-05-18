import logging
from pprint import PrettyPrinter

from troposphere import GetAtt, Ref, StackName, backup

log = logging.getLogger(__name__)
pp = PrettyPrinter(indent=3)


def backup_vault():
  return backup.BackupVault(
      'BackupVault',
      BackupVaultName=StackName,
      BackupVaultTags={
          'mm:stack': StackName,
      })


def backup_plan(backup_vault):
  return backup.BackupPlan(
      'BackupPlan',
      BackupPlan=backup.BackupPlanResourceType(
          BackupPlanName=StackName,
          BackupPlanRule=[
              backup.BackupRuleResourceType(
                  CompletionWindowMinutes=60.0 * 23,
                  Lifecycle=backup.LifecycleResourceType(DeleteAfterDays=31.0),
                  RecoveryPointTags={
                      'mm:stack': StackName,
                  },
                  RuleName='daily',
                  ScheduleExpression='cron(0 18 * * ? *)',
                  StartWindowMinutes=60.0,
                  TargetBackupVault=GetAtt(backup_vault, 'BackupVaultName')),
          ]),
      BackupPlanTags={
          'mm:stack': StackName,
      })


def backup_selection(
    *, backup_plan, backup_role, config_volume_stack, db_volume_stack):
  return backup.BackupSelection(
      'BackupSelection',
      BackupPlanId=GetAtt(backup_plan, 'BackupPlanId'),
      BackupSelection=backup.BackupSelectionResourceType(
          Conditions=backup.Conditions(
              StringEquals=[
                  backup.ConditionParameter(
                      ConditionKey='aws:ResourceTag/mm:backup',
                      ConditionValue='true'),
              ]),
          IamRoleArn=GetAtt(backup_role, 'Arn'),
          ListOfTags=[
              backup.ConditionResourceType(
                  ConditionKey='mm:stack',
                  ConditionType='STRINGEQUALS',
                  ConditionValue=StackName),
              backup.ConditionResourceType(
                  ConditionKey='mm:stack',
                  ConditionType='STRINGEQUALS',
                  ConditionValue=Ref(config_volume_stack)),
              backup.ConditionResourceType(
                  ConditionKey='mm:stack',
                  ConditionType='STRINGEQUALS',
                  ConditionValue=Ref(db_volume_stack)),
          ],
          SelectionName='default'))
