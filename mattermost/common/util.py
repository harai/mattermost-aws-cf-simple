import hashlib
from datetime import datetime
from itertools import chain

from troposphere import (
    Base64,
    GetAtt,
    ImportValue,
    Join,
    Parameter,
    Ref,
    Region,
    Select,
    Split,
    StackId,
    StackName,
    Sub,
    certificatemanager,
    ec2,
    iam,
    imagebuilder,
    logs,
    s3,
    sns
)


def command(c, cwd=None):
  d = {'command': c}
  if cwd is not None:
    d['cwd'] = cwd
  return d


def userdata(ini_resource, sig_resource, fingerprint_dict):
  fp_comments = list(
      chain.from_iterable(
          ['# {}: '.format(k), v, '\n']
          for k, v in sorted(fingerprint_dict.items())))

  return Base64(
      Sub(
          get_file('mattermost/common/resources/userdata'),
          STACK_NAME=StackName,
          STACK_ID=StackId,
          REGION=Region,
          INI_RESOURCE=ini_resource,
          SIG_RESOURCE=sig_resource,
          LAUNCH_CONFIG_FINGERPRINT=Join('', fp_comments)))


def get_file(path):
  with open(path, 'r') as f:
    return f.read()


def condition(template, name, cond):
  template.add_condition(name, cond)
  return name


class Imp(object):

  def __init__(self, stack_name_value):
    self.stack_name_value = stack_name_value

  def ort(self, name):
    return ImportValue(
        Sub('${{stack}}:{}'.format(name), stack=self.stack_name_value))

  @classmethod
  def from_ref(cls, stack_name):
    return cls(Ref(stack_name))


def sha1digest(data):
  if isinstance(data, str):
    data = bytes(data, 'utf-8')
  return hashlib.sha1(data).hexdigest()


def current_time():
  return datetime.now().strftime('%Y%m%d%H%M%S')


def commandname(no, name):
  return '{:06d}-{}'.format(no, name)


def lambda_log_name(function):
  return Sub('/aws/lambda/${f}', f=Ref(function))


resource_arns = {
    certificatemanager.Certificate: lambda r: Ref(r),
    ec2.EIP: lambda r: Sub(
        (
            'arn:${AWS::Partition}:ec2:${AWS::Region}:${AWS::AccountId}:'
            'elastic-ip/${eip}'),
        eip=GetAtt(r, 'AllocationId')),
    iam.InstanceProfile: lambda r: GetAtt(r, 'Arn'),
    iam.ManagedPolicy: lambda r: Ref(r),
    iam.Role: lambda r: GetAtt(r, 'Arn'),
    imagebuilder.Component: lambda r: GetAtt(r, 'Arn'),
    imagebuilder.ImageRecipe: lambda r: GetAtt(r, 'Arn'),
    imagebuilder.InfrastructureConfiguration: lambda r: GetAtt(r, 'Arn'),
    logs.LogGroup: lambda r: Select(0, Split(':*', GetAtt(r, 'Arn'))),
    s3.Bucket: lambda r: GetAtt(r, 'Arn'),
    sns.Topic: lambda r: Ref(r),
}

resource_names = {
    ec2.EIP: lambda r: GetAtt(r, 'AllocationId'),
    ec2.InternetGateway: lambda r: Ref(r),
    ec2.LaunchTemplate: lambda r: Ref(r),
    ec2.RouteTable: lambda r: Ref(r),
    ec2.SecurityGroup: lambda r: Ref(r),
    ec2.Subnet: lambda r: Ref(r),
    ec2.Volume: lambda r: Ref(r),
    ec2.VPC: lambda r: Ref(r),
    iam.AccessKey: lambda r: Ref(r),
    iam.InstanceProfile: lambda r: Ref(r),
    iam.Role: lambda r: Ref(r),
    logs.LogGroup: lambda r: Select(0, Split(':*', Ref(r))),
    s3.Bucket: lambda r: Ref(r),
}


def arn_of(res):
  return resource_arns[type(res)](res)


def name_of(res):
  return resource_names[type(res)](res)


def read_param(res):
  if isinstance(res, Parameter):
    return Ref(res)
  raise TypeError()
