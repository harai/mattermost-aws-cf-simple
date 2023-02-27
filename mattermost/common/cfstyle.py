import logging
import os
import subprocess
from pprint import PrettyPrinter

from troposphere import Join, Output, Parameter, Ref, Template, constants

log = logging.getLogger(__name__)
pp = PrettyPrinter(indent=3)


class ParamUi(object):

  def __init__(self):
    self._meta_groups = []
    self._meta_labels = {}
    self._parameters = []

  def group(self, template, label, params):
    self._meta_groups.append(
        {
            'Label': {
                'default': label
            },
            'Parameters': [p['parameter'].name for p in params],
        })
    self._meta_labels.update(
        {p['parameter'].name: {
            'default': p['label']
        } for p in params})

    ps = [template.add_parameter(p['parameter']) for p in params]
    self._parameters.extend(ps)
    return ps

  def output(self, template):
    template.set_metadata(
        {
            'AWS::CloudFormation::Interface': {
                'ParameterGroups': self._meta_groups,
                'ParameterLabels': self._meta_labels,
            },
        })

  def fingerprint(self):
    ss = []
    for p in self._parameters:
      ss.append(p.name + ':')
      if p.Type in [
          constants.COMMA_DELIMITED_LIST,
          constants.LIST_OF_NUMBERS,
      ] or p.Type.startswith('List<'):
        ss.append(Join('\t', Ref(p)))
      else:
        ss.append(Ref(p))
    return Join('\n', ss)


def current_git_revision():
  if 'CI' in os.environ:
    return os.environ['COMMIT_SHA']

  p = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
  return p.stdout.decode().strip()


def uncommitted_changes():
  if 'CI' in os.environ:
    return '[all committed]'

  p = subprocess.run(
      ['git', 'diff', 'HEAD', '--name-status'], stdout=subprocess.PIPE)
  s = p.stdout.decode().strip()
  return '[all committed]' if s == '' else '[with uncommitted changes]'


def version_info():
  return 'Build URL: {}, Git revision: {} {}'.format(
      os.environ.get('BUILD_URL', 'None'), current_git_revision(),
      uncommitted_changes())


def version_short():
  url = os.environ.get('BUILD_URL')
  if url is None:
    return '(None)'
  return url.split('/tag/')[1]


def template_type_group(pui, template, name):
  return pui.group(
      template, 'Template Type', [
          {
              'parameter': Parameter(
                  'TemplateType',
                  Description=(
                      'Current template type.  '
                      'This field is used to validate the same type of '
                      'template is used when updating to a different version.'),
                  AllowedValues=[name],
                  Default=name,
                  Type=constants.STRING),
              'label': 'Template Type',
          },
      ])


def version(ver):
  return Output('Version', Value=ver)


def template(name):
  ver = version_info()
  t = Template('{} - {}'.format(name, ver))
  pui = ParamUi()
  [_] = template_type_group(pui, t, name)
  t.add_output(version(ver))

  return t, pui
