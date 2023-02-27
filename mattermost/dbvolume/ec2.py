from troposphere import If, NoValue, ec2

from mattermost.common import util


def volume(*, az, size, snapshot_id, use_snapshot):
  return ec2.Volume(
      'Volume',
      AvailabilityZone=util.read_param(az),
      Size=util.read_param(size),
      SnapshotId=If(use_snapshot, util.read_param(snapshot_id), NoValue),
      VolumeType='gp3')
