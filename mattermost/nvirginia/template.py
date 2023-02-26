from mattermost.common.template import Template
from mattermost.nvirginia import s3


class NvirginiaTemplate(Template):

  name: str = 'Mattermost NVirginia'

  def definition(self) -> None:
    s3.my_bucket(self)
