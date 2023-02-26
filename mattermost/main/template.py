from mattermost.common.template import Template
from mattermost.main import s3


class MainTemplate(Template):

  name: str = 'Mattermost Main'

  def definition(self) -> None:
    s3.my_bucket(self)
