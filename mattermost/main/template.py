from mattermost.common import cfstyle
from mattermost.main import s3


def construct_template():
  t, pui = cfstyle.template('Mattermost Main')

  pui.output(t)

  t.add_resource(s3.my_bucket())

  return t


if __name__ == '__main__':
  print(construct_template().to_json(indent=2))
