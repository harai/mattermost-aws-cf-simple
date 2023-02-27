from troposphere import Parameter, constants


def domain_group(pui, template):
  return pui.group(
      template, 'Domain', [
          {
              'parameter': Parameter(
                  'Domain',
                  Description='Domain name for Mattermost',
                  Type=constants.STRING),
              'label': 'Domain',
          },
      ])
