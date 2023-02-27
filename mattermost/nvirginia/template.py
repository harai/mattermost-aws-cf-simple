from mattermost.common import cfstyle
from mattermost.nvirginia import acm, output, parameter


def construct_template():
  t, pui = cfstyle.template('Mattermost NVirginia')

  [domain] = parameter.domain_group(pui, t)

  pui.output(t)

  global_certificate = t.add_resource(acm.global_certificate(domain))

  t.add_output(output.global_certificate_arn(global_certificate))

  return t


if __name__ == '__main__':
  print(construct_template().to_json(indent=2))
