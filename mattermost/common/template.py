from abc import abstractmethod

from aws_cdk import Aws, Stack, Tags
from constructs import Construct


class Template(Stack):

  def __init__(self, scope: Construct, **kwargs) -> None:
    kebab_case = self.name.lower().replace(' ', '-')
    dot_case = self.name.lower().replace(' ', '.')
    super().__init__(scope, id=dot_case, stack_name=kebab_case, **kwargs)

    Tags.of(self).add('stack', Aws.STACK_NAME)
    self.definition()

  @abstractmethod
  def definition(self) -> None:
    raise NotImplementedError()

  @property
  @abstractmethod
  def name(self) -> str:
    raise NotImplementedError()
