from troposphere import GetAtt, StackName, Sub, autoscaling
from troposphere.policies import (
    AutoScalingCreationPolicy,
    AutoScalingRollingUpdate,
    CreationPolicy,
    ResourceSignal,
    UpdatePolicy
)

from mattermost.common import util


def auto_scaling_group(
    *, route_internet, subnet_route_table_association, az, subnet, eip,
    launch_template, notification_topic):
  return autoscaling.AutoScalingGroup(
      'AutoScalingGroup',
      DependsOn=[
          eip.name,
          route_internet,
          subnet_route_table_association,
      ],
      AvailabilityZones=[util.read_param(az)],
      Cooldown='180',
      DesiredCapacity='1',
      HealthCheckGracePeriod='120',
      HealthCheckType='EC2',
      LaunchTemplate=autoscaling.LaunchTemplateSpecification(
          LaunchTemplateId=util.name_of(launch_template),
          Version=GetAtt(launch_template, 'LatestVersionNumber'),
      ),
      MaxSize=1,
      MetricsCollection=[autoscaling.MetricsCollection(Granularity='1Minute')],
      MinSize=0,
      NotificationConfigurations=[
          autoscaling.NotificationConfigurations(
              NotificationTypes=[
                  autoscaling.EC2_INSTANCE_LAUNCH_ERROR,
                  autoscaling.EC2_INSTANCE_TERMINATE_ERROR,
              ],
              TopicARN=util.arn_of(notification_topic)),
      ],
      Tags=autoscaling.Tags(
          **{
              'Name': Sub('${AWS::StackName}:AutoScalingGroup'),
              'mm:stack': StackName,
          }),
      VPCZoneIdentifier=[util.name_of(subnet)],
      CreationPolicy=CreationPolicy(
          ResourceSignal=ResourceSignal(Timeout='PT30M', Count=1),
          AutoScalingCreationPolicy=AutoScalingCreationPolicy(
              MinSuccessfulInstancesPercent=100)),
      # ConfigVolume and DBVolume are mutex resources and not allowed to
      # be associated with more than one EC2 instance.
      #
      # Note EIP is not a mutex resource since it doesn't prevent EC2
      # instance from starting.
      UpdatePolicy=UpdatePolicy(
          AutoScalingRollingUpdate=AutoScalingRollingUpdate(
              MinInstancesInService=0)))
