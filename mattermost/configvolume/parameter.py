from troposphere import Parameter, constants


def volume_group(pui, template):
  return pui.group(
      template, 'Volume', [
          {
              'parameter': Parameter(
                  'Az',
                  Description='Availability Zone where the volume is created',
                  Type=constants.AVAILABILITY_ZONE_NAME),
              'label': 'Availability Zone',
          },
          {
              'parameter': Parameter(
                  'Size',
                  Default='1',
                  Description='Size for volume',
                  MinValue=1,
                  Type=constants.NUMBER),
              'label': 'Size (GB)',
          },
      ])


def snapshot_group(pui, template):
  return pui.group(
      template, 'Snapshot (Optional)', [
          {
              'parameter': Parameter(
                  'SnapshotId',
                  Description=(
                      'Create a new volume from an existing snapshot. '
                      'You cannot change this value once created.'),
                  Type=constants.STRING),
              'label': 'Snapshot ID',
          },
      ])
