import base64
import logging
from pprint import PrettyPrinter

from troposphere import If, NoValue, Sub, cloudformation

from mattermost.common import util

log = logging.getLogger(__name__)
pp = PrettyPrinter(indent=3)


class InitItem(object):

  def __init__(
      self,
      name,
      path=None,
      body=None,
      as_bash=False,
      params=None,
      service=None,
      copy_as_base64=False):
    self._name = name
    self._path = path
    self._body = body
    self._params = params
    self._as_bash = as_bash
    self._service = service
    self._copy_as_base64 = copy_as_base64

  @property
  def name(self):
    return self._name

  @property
  def service(self):
    return self._service

  @property
  def content(self):
    if self._path is not None:
      c = util.get_file(self._path)
    elif self._body is not None:
      c = self._body
    else:
      raise ValueError(self._name)

    c2 = (
        "#!/bin/sh\n\n/bin/bash -O inherit_errexit -eux <<'CF_EOF'\n" + c +
        "\nCF_EOF\n" if self._as_bash else c)

    c3 = Sub(c2, **self._params) if self._params is not None else c2

    if self._copy_as_base64:
      return base64.b64encode(c3.encode()).decode()

    return c3


class InitFile(InitItem):

  def __init__(
      self,
      name,
      path=None,
      body=None,
      params=None,
      mode='000644',
      service=None,
      owner='root',
      copy_as_base64=False):
    super().__init__(
        name=name,
        path=path,
        body=body,
        params=params,
        service=service,
        copy_as_base64=copy_as_base64)

    self._mode = mode
    self._owner = owner

  @property
  def prop(self):
    return cloudformation.InitFile(
        content=self.content,
        mode=self._mode,
        owner=self._owner,
        group=self._owner)

  @classmethod
  def from_dict(cls, d):
    return cls(
        d['name'],
        path=d.get('path'),
        body=d.get('body'),
        params=d.get('params'),
        mode=d.get('mode', '000644'),
        service=d.get('service'),
        owner=d.get('owner', 'root'),
        copy_as_base64=d.get('copy_as_base64', False))


class InitFileUrl:

  def __init__(self, name, source, mode='000644', service=None, owner='root'):
    self._name = name
    self._source = source
    self._service = service
    self._mode = mode
    self._owner = owner

  @property
  def name(self):
    return self._name

  @property
  def service(self):
    return self._service

  @property
  def prop(self):
    return cloudformation.InitFile(
        source=self._source,
        mode=self._mode,
        owner=self._owner,
        group=self._owner)

  @classmethod
  def from_dict(cls, d):
    return cls(
        d['name'],
        source=d['source'],
        mode=d.get('mode', '000644'),
        service=d.get('service'),
        owner=d.get('owner', 'root'))


class InitCommand(InitItem):

  def __init__(
      self,
      name,
      path=None,
      body=None,
      as_bash=False,
      params=None,
      service=None,
      cwd=None):
    super().__init__(
        name=name,
        path=path,
        body=body,
        as_bash=as_bash,
        params=params,
        service=service)

    self._cwd = cwd

  @property
  def prop(self):
    prop = {'command': self.content}
    if self._cwd is not None:
      prop['cwd'] = self._cwd

    return prop

  @classmethod
  def from_dict(cls, d):
    return cls(
        d['name'],
        path=d.get('path'),
        body=d.get('body'),
        as_bash=d.get('as_bash', False),
        params=d.get('params'),
        service=d.get('service'),
        cwd=d.get('cwd'))


class Init(object):

  def __init__(self):
    self._files = []
    self._files_if = []
    self._commands = []
    self._commands_if = []

  def add_files(self, files):
    self._files += (InitFile.from_dict(f) for f in files)

  def add_file(self, file):
    self.add_files([file])

  def add_file_urls(self, urls):
    self._files += (InitFileUrl.from_dict(f) for f in urls)

  def add_file_url(self, url):
    self.add_file_urls([url])

  def add_file_if(self, condition, true_file=None, false_file=None):
    self._files_if += [
        (
            condition,
            (None if true_file is None else InitFile.from_dict(true_file)),
            (None if false_file is None else InitFile.from_dict(false_file)))
    ]

  def add_commands(self, commands):
    self._commands += (InitCommand.from_dict(c) for c in commands)

  def add_command(self, command):
    self.add_commands([command])

  def add_command_if(self, condition, true_command=None, false_command=None):
    self._commands_if += [
        (
            condition, (
                None if true_command is None else
                InitCommand.from_dict(true_command)), (
                    None if false_command is None else
                    InitCommand.from_dict(false_command)))
    ]

  def files(self):
    d = {f.name: f.prop for f in self._files}
    d.update(
        {
            (ff if tf is None else tf).name: If(
                c, NoValue if tf is None else tf.prop,
                NoValue if ff is None else ff.prop)
            for c, tf, ff in self._files_if
        })
    return d

  def commands(self):
    d = {c.name: c.prop for c in self._commands}
    d.update(
        {
            (fc if tc is None else tc).name: If(
                c, NoValue if tc is None else tc.prop,
                NoValue if fc is None else fc.prop)
            for c, tc, fc in self._commands_if
        })
    return d
