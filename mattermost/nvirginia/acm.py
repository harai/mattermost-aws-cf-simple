from troposphere import StackName, Tags, certificatemanager

from mattermost.common import util


def global_certificate(domain):
  return certificatemanager.Certificate(
      'GlobalCertificate',
      DomainName=util.read_param(domain),
      Tags=Tags({
          'mm:stack': StackName,
      }),
      ValidationMethod='DNS')
