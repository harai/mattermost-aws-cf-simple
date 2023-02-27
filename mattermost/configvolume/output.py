from troposphere import Export, Output, Sub

from mattermost.common import util


def export(name):
  return Export(Sub('${AWS::StackName}:${name}', name=name))


def volume(volume):
  return Output(
      'DataVolume', Value=util.name_of(volume), Export=export('DataVolume'))
