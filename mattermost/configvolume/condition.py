from troposphere import Equals, Not

from mattermost.common import util


def use_snapshot(snapshot_id):
  return Not(Equals(util.read_param(snapshot_id), ''))
