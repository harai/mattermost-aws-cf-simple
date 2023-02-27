from mattermost.common import cfstyle, util
from mattermost.dbvolume import condition, ec2, output, parameter


def construct_template():
  t, pui = cfstyle.template('Mattermost DBVolume')

  # Parameters
  [az, size] = parameter.volume_group(pui, t)
  [snapshot_id] = parameter.snapshot_group(pui, t)
  pui.output(t)

  # Conditions
  use_snapshot = util.condition(
      t, 'UseSnapshot', condition.use_snapshot(snapshot_id))

  # EC2
  volume = t.add_resource(
      ec2.volume(
          az=az, size=size, snapshot_id=snapshot_id, use_snapshot=use_snapshot))

  # Output
  t.add_output(output.volume(volume))

  return t


if __name__ == '__main__':
  print(construct_template().to_json(indent=2))
