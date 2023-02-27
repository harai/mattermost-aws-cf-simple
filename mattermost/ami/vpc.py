import logging
from pprint import PrettyPrinter

from troposphere import Sub, ec2

from mattermost.common import util

log = logging.getLogger(__name__)
pp = PrettyPrinter(indent=3)


def my_vpc(vpc_cidr_block):
  return ec2.VPC(
      'Vpc',
      CidrBlock=Sub(
          '10.${block}.0.0/16', block=util.read_param(vpc_cidr_block)),
      EnableDnsHostnames=True,
      EnableDnsSupport=True,
      InstanceTenancy='default')


def subnet(my_vpc, vpc_cidr_block, az):
  return ec2.Subnet(
      'Subnet',
      AvailabilityZone=util.read_param(az),
      CidrBlock=Sub(
          '10.${block}.0.0/24', block=util.read_param(vpc_cidr_block)),
      MapPublicIpOnLaunch=True,
      VpcId=util.name_of(my_vpc),
  )


def route_table(my_vpc):
  return ec2.RouteTable('RouteTable', VpcId=util.name_of(my_vpc))


def route_internet(vpc_gateway_attachment, route_table, internet_gateway):
  return ec2.Route(
      'RouteDefault',
      DependsOn=vpc_gateway_attachment.name,
      DestinationCidrBlock='0.0.0.0/0',
      GatewayId=util.name_of(internet_gateway),
      RouteTableId=util.name_of(route_table),
  )


def internet_gateway():
  return ec2.InternetGateway('InternetGateway')


def vpc_gateway_attachment(my_vpc, internet_gateway):
  return ec2.VPCGatewayAttachment(
      'VpcGatewayAttachment',
      InternetGatewayId=util.name_of(internet_gateway),
      VpcId=util.name_of(my_vpc),
  )


def subnet_route_table_association(route_table, subnet):
  return ec2.SubnetRouteTableAssociation(
      'SubnetRouteTableAssociation',
      RouteTableId=util.name_of(route_table),
      SubnetId=util.name_of(subnet),
  )


def ssh_security_group(my_vpc):
  return ec2.SecurityGroup(
      'SshSecurityGroup',
      GroupDescription='Allow SSH',
      SecurityGroupEgress=[],
      SecurityGroupIngress=[
          ec2.SecurityGroupRule(
              IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0'),
      ],
      VpcId=util.name_of(my_vpc))
