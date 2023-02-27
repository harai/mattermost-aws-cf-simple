from troposphere import certificatemanager

from mattermost.common import util


def global_certificate(domain):
  return certificatemanager.Certificate(
      'GlobalCertificate',
      DomainName=util.read_param(domain),
      ValidationMethod='DNS')
