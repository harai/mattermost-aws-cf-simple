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


def general_group(pui, template):
  return pui.group(
      template, 'General', [
          {
              'parameter': Parameter('BaseAmi', Type=constants.IMAGE_ID),
              'label': 'Base AMI',
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
              'parameter': Parameter(
                  'MattermostVersion', Type=constants.STRING),
              'label': 'Mattermost Version',
          },
      ])
