from troposphere import Parameter, constants


def network_group(pui, template):
  return pui.group(
      template, 'Network', [
          {
              'parameter': Parameter(
                  'VpcCidrBlock',
                  Description=(
                      'The second octet of CIDR Block used for VPC, '
                      'which is N in "10.N.0.0/16"'),
                  Type=constants.NUMBER),
              'label': 'VPC CIDR Block',
          },
          {
              'parameter': Parameter(
                  'Az',
                  Description=('Availability Zone to use'),
                  Type=constants.AVAILABILITY_ZONE_NAME),
              'label': 'Availability Zone',
          },
      ])


def volume_group(pui, template):
  return pui.group(
      template, 'Volumes', [
          {
              'parameter': Parameter(
                  'ConfigVolumeStack', Type=constants.STRING),
              'label': 'ConfigVolume Stack Name',
          },
          {
              'parameter': Parameter('DbVolumeStack', Type=constants.STRING),
              'label': 'DBVolume Stack Name',
          },
      ])


def general_group(pui, template):
  return pui.group(
      template, 'General', [
          {
              'parameter': Parameter('Domain', Type=constants.STRING),
              'label': 'Domain Name',
          },
          {
              'parameter': Parameter('Ami', Type=constants.IMAGE_ID),
              'label': 'AMI ID (Amazon Linux 2023 x86_64)',
          },
          {
              'parameter': Parameter('KeyPair', Type=constants.KEY_PAIR_NAME),
              'label': 'Key Pair',
          },
          {
              'parameter': Parameter(
                  'NotificationEmail', Type=constants.STRING),
              'label': 'Notification Email',
          },
          {
              'parameter': Parameter('InstanceType', Type=constants.STRING),
              'label': 'EC2 Instance Type',
          },
          {
              'parameter': Parameter(
                  'InstanceFingerprint', Type=constants.STRING),
              'label': 'EC2 Instance Fingerprint',
          },
      ])
