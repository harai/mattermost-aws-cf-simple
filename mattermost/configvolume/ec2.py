from troposphere import If, NoValue, StackName, Sub, Tags, ec2

from mattermost.common import util


def volume(*, az, size, snapshot_id, use_snapshot):
  return ec2.Volume(
      'Volume',
      AvailabilityZone=util.read_param(az),
      Size=util.read_param(size),
      SnapshotId=If(use_snapshot, util.read_param(snapshot_id), NoValue),
      Tags=Tags(
          {
              'Name': Sub('${AWS::StackName}:Volume'),
              'mm:backup': 'true',
              'mm:stack': StackName,
          }),
      VolumeType='gp3')
