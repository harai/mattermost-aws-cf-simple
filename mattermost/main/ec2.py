import string

from troposphere import (
    FindInMap,
    GetAtt,
    Ref,
    Region,
    StackName,
    Sub,
    Tags,
    cloudformation,
    ec2
)

from mattermost.common import util
from mattermost.common.ec2init import Init
from mattermost.main.config import (
    DEVICE_CONFIG,
    DEVICE_CONFIG_XVD,
    DEVICE_DB,
    DEVICE_DB_XVD,
    DEVICE_ROOT,
    DEVICE_ROOT_SIZE,
    DEVICE_ROOT_XVD,
    DEVICE_SWAP_XVD
)


def my_vpc(vpc_cidr_block):
  return ec2.VPC(
      'MyVpc',
      CidrBlock=Sub(
          '10.${block}.0.0/16', block=util.read_param(vpc_cidr_block)),
      EnableDnsHostnames=True,
      EnableDnsSupport=True,
      InstanceTenancy='default',
      Tags=Tags(
          {
              'Name': Sub('${AWS::StackName}:MyVpc'),
              'mm:stack': StackName,
          }))


def subnet(my_vpc, vpc_cidr_block, az):
  return ec2.Subnet(
      'Subnet',
      AvailabilityZone=util.read_param(az),
      CidrBlock=Sub(
          '10.${block}.0.0/24', block=util.read_param(vpc_cidr_block)),
      MapPublicIpOnLaunch=True,
      Tags=Tags(
          {
              'Name': Sub('${AWS::StackName}:Subnet'),
              'mm:stack': StackName,
          }),
      VpcId=util.name_of(my_vpc))


def route_table(my_vpc):
  return ec2.RouteTable('RouteTable', VpcId=util.name_of(my_vpc))


def route_internet(*, vpc_gateway_attachment, route_table, internet_gateway):
  return ec2.Route(
      'RouteDefault',
      DependsOn=vpc_gateway_attachment.name,
      DestinationCidrBlock='0.0.0.0/0',
      GatewayId=util.name_of(internet_gateway),
      RouteTableId=util.name_of(route_table),
  )


def internet_gateway():
  return ec2.InternetGateway(
      'InternetGateway',
      Tags=Tags(
          {
              'Name': Sub('${AWS::StackName}:InternetGateway'),
              'mm:stack': StackName,
          }))


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
      GroupDescription='Incoming SSH connection',
      SecurityGroupEgress=[],
      SecurityGroupIngress=[
          ec2.SecurityGroupRule(
              IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0'),
      ],
      Tags=Tags(
          {
              'Name': Sub('${AWS::StackName}:SshSecurityGroup'),
              'mm:stack': StackName,
          }),
      VpcId=util.name_of(my_vpc))


def web_security_group(my_vpc):
  return ec2.SecurityGroup(
      'WebSecurityGroup',
      GroupDescription='Incoming web requests',
      SecurityGroupEgress=[],
      SecurityGroupIngress=[
          # ec2.SecurityGroupRule(
          #     CidrIp='0.0.0.0/0', FromPort=443, IpProtocol='tcp', ToPort=443),
          # ec2.SecurityGroupRule(
          #     CidrIp='0.0.0.0/0', FromPort=80, IpProtocol='tcp', ToPort=80),
          ec2.SecurityGroupRule(
              SourcePrefixListId=FindInMap(
                  'RegionMap', Region, 'CloudfrontPrefixList'),
              FromPort=443,
              IpProtocol='tcp',
              ToPort=443),
      ],
      VpcId=util.name_of(my_vpc),
      Tags=Tags(
          {
              'Name': Sub('${AWS::StackName}:WebSecurityGroup'),
              'mm:stack': StackName,
          }),
  )


def eip(vpc):
  return ec2.EIP(
      'Eip',
      Domain=Ref(vpc),
      Tags=Tags({
          'Name': Sub('${AWS::StackName}:Eip'),
          'mm:stack': StackName,
      }))


class Template(string.Template):
  delimiter = '%%'


def template(path, params):
  return Template(util.get_file(path)).substitute(params)


MYSQL_HOME = '/var/lib/mysql'
MYSQL_DATA = '/var/lib/mysql/data'
MYSQL_CONFIG = '/var/lib/mysql/persist'
MNT_CONFIG = '/mnt/config'
MNT_MM = '/mnt/config/mattermost'
MNT_MYSQL = '/mnt/config/mysql'
MNT_LE = '/mnt/config/letsencrypt'
MM_CONFIG = '/var/opt/mattermost/persist'
LE_CONFIG = '/etc/letsencrypt'


def ec2_metadata(
    *,
    cfninit_log,
    mattermost_log,
    mysql_error_log,
    config_volume_value,
    db_volume_value,
    eip,
    domain,
    file_bucket,
    mail_access_key,
    email,
):

  def logger_init():
    init = Init()
    init.add_files(
        [
            {
                'name': '/var/opt/cwagent/config.json',
                'path': 'mattermost/main/resources/files/cwagent.json',
                'params': {
                    'CFNINIT_LOG': util.name_of(cfninit_log),
                    'MATTERMOST_LOG': util.name_of(mattermost_log),
                    'MYSQL_ERROR_LOG': util.name_of(mysql_error_log),
                },
            },
        ])

    init.add_command(
        {
            'name': util.commandname(1, 'start-cwagent'),
            'body': (
                '/opt/aws/amazon-cloudwatch-agent/bin/'
                'amazon-cloudwatch-agent-ctl'
                ' -a fetch-config -m ec2 -s -c'
                ' file:/var/opt/cwagent/config.json'),
        })

    return init

  def fs_init():
    init = Init()
    init.add_files(
        [
            {
                'name': '/etc/cron.d/put-metric.conf',
                'path': 'mattermost/main/resources/files/put-metric.conf',
            },
            {
                'name': '/etc/cron.d/reassoc-eip.conf',
                'path': 'mattermost/main/resources/files/reassoc-eip.conf',
            },
            {
                'name': '/home/ec2-user/.bashrc.d/default',
                'path': 'mattermost/main/resources/files/bashrc.sh',
                'params': {
                    'STACK_NAME': StackName,
                },
            },
            {
                'name': '/usr/local/bin/reassoc-eip',
                'path': 'mattermost/main/resources/files/reassoc-eip',
                'mode': '000755',
                'params': {
                    'ALLOCATION': util.name_of(eip),
                },
            },
            {
                'name': '/etc/logrotate.d/cwagent',
                'path': 'mattermost/main/resources/files/cwagent.logrotate',
            },
            {
                'name': '/etc/logrotate.d/mattermost',
                'path': 'mattermost/main/resources/files/mattermost.logrotate',
            },
        ])

    init.add_commands(
        [
            {
                'name': util.commandname(1, 'makeswap'),
                'body': 'mkswap {0} && swapon {0}'.format(DEVICE_SWAP_XVD),
            },
            {
                'name': util.commandname(2, 'mkdir-config'),
                'body': (
                    f'mkdir -p {MNT_CONFIG} {MM_CONFIG} {LE_CONFIG} && '
                    f'chown -R mm: {MM_CONFIG}'),
            },
            {
                'name': util.commandname(2, 'mkdir-db'),
                'body': (
                    f'rm -fr {MYSQL_HOME} && '
                    f'mkdir -p {MYSQL_DATA} {MYSQL_CONFIG} && '
                    f'chown -R mysql: {MYSQL_HOME}'),
            },
            {
                'name': util.commandname(3, 'attach-ebs-config'),
                'body': template(
                    'mattermost/main/resources/commands/attach-ebs', {
                        'DEVICE': DEVICE_CONFIG_XVD,
                    }),
                'as_bash': True,
                'params': {
                    'VOLUME': config_volume_value,
                },
            },
            {
                'name': util.commandname(3, 'attach-ebs-db'),
                'body': template(
                    'mattermost/main/resources/commands/attach-ebs', {
                        'DEVICE': DEVICE_DB_XVD,
                    }),
                'as_bash': True,
                'params': {
                    'VOLUME': db_volume_value,
                },
            },
            {
                # It takes some time for devices to become available.
                'name': util.commandname(4, 'sleep'),
                'body': 'sleep 20',
            },
            {
                'name': util.commandname(5, 'mount-ebs-config'),
                'body': template(
                    'mattermost/main/resources/commands/mount-ebs', {
                        'DEVICE': DEVICE_CONFIG,
                        'MOUNT': MNT_CONFIG,
                    }),
                'as_bash': True,
            },
            {
                'name': util.commandname(5, 'mount-ebs-db'),
                'body': template(
                    'mattermost/main/resources/commands/mount-ebs', {
                        'DEVICE': DEVICE_DB,
                        'MOUNT': MYSQL_DATA,
                    }),
                'as_bash': True,
            },
            {
                'name': util.commandname(6, 'bind-config'),
                'body': (
                    f'mkdir -p {MNT_MM} {MNT_MYSQL} {MNT_LE} && '
                    f'chown -R mm: {MNT_MM} && chown -R mysql: {MNT_MYSQL} && '
                    f'mount --bind {MNT_MM} {MM_CONFIG} && '
                    f'mount --bind {MNT_LE} {LE_CONFIG} && '
                    f'mount --bind {MNT_MYSQL} {MYSQL_CONFIG}'),
            },
        ])

    return init

  def mysql_init():
    init = Init()
    init.add_files(
        [
            {
                'name': '/etc/my.cnf.d/mysqld.cnf',
                'path': 'mattermost/main/resources/files/mysqld.cnf',
            },
        ])

    init.add_commands(
        [
            {
                'name': util.commandname(1, 'change-owner'),
                'body': (
                    'mkdir -p /var/log/mysql && '
                    'chown mysql: /var/log/mysql /var/lib/mysql/data'),
            },
            {
                'name': util.commandname(2, 'remove-default-config'),
                'body': 'rm /etc/my.cnf.d/community-mysql-server.cnf',
            },
            {
                'name': util.commandname(3, 'init-mysql'),
                'body': template(
                    'mattermost/main/resources/commands/init-mysql', {
                        'SQL': util.get_file(
                            'mattermost/main/resources/commands/mysql-init.sql'
                        ),
                    }),
                'as_bash': True,
            },
        ])

    return init

  def web_init():
    init = Init()
    init.add_files(
        [
            {
                'name': '/etc/cron.d/acme-renew.conf',
                'path': 'mattermost/main/resources/files/acme-renew.conf',
                'params': {
                    'EMAIL': util.read_param(email),
                    'DOMAIN': util.read_param(domain),
                },
            },
            {
                'name': '/etc/nginx/nginx.conf',
                'path': 'mattermost/main/resources/files/nginx.conf',
                'params': {
                    'DOMAIN': util.read_param(domain),
                },
            },
            {
                'name': '/lib/systemd/system/mattermost.service',
                'path': 'mattermost/main/resources/files/mattermost.service',
            },
            {
                'name': '/usr/local/bin/put-metric',
                'path': 'mattermost/main/resources/files/put-metric',
                'params': {
                    'CONFIG_DEVICE': DEVICE_CONFIG,
                    'DB_DEVICE': DEVICE_DB,
                    'DOMAIN': util.read_param(domain),
                    'ROOT_DEVICE': DEVICE_ROOT,
                },
                'mode': '000755',
            },
        ])

    init.add_commands(
        [
            {
                'name': util.commandname(1, 'config-mattermost'),
                'path': 'mattermost/main/resources/commands/config-mattermost',
                'as_bash': True,
                'params': {
                    'DOMAIN': util.read_param(domain),
                    'BUCKET': util.name_of(file_bucket),
                    'SMTP_USER': util.name_of(mail_access_key),
                    'SMTP_SERVER': FindInMap(
                        'RegionMap', Region, 'SesSmtpServer'),
                    'SMTP_PASSWORD': GetAtt(mail_access_key, 'SecretAccessKey'),
                },
            },
            {
                'name': util.commandname(2, 'allow-bind'),
                'body': (
                    'setcap cap_net_bind_service+ep '
                    '/opt/mattermost/bin/mattermost'),
            },
            {
                'name': util.commandname(3, 'acme'),
                'body': (
                    "certbot certonly --dns-route53 -n -m '${EMAIL}' "
                    '--agree-tos --expand '
                    "-d '${DOMAIN},origin.${AWS::StackName}.${DOMAIN}'"),
                'params': {
                    'EMAIL': util.read_param(email),
                    'DOMAIN': util.read_param(domain),
                },
            },
            {
                'name': util.commandname(4, 'eip'),
                'path': 'mattermost/main/resources/commands/eip',
                'as_bash': True,
                'params': {
                    'ALLOCATION': util.name_of(eip),
                },
            },
        ])

    return init

  logger = logger_init()
  fs = fs_init()
  mysql = mysql_init()
  web = web_init()

  return cloudformation.Init(
      cloudformation.InitConfigSets(default=[
          'logger',
          'fs',
          'mysql',
          'web',
      ]),
      logger=cloudformation.InitConfig(
          files=logger.files(), commands=logger.commands()),
      fs=cloudformation.InitConfig(files=fs.files(), commands=fs.commands()),
      mysql=cloudformation.InitConfig(
          files=mysql.files(), commands=mysql.commands()),
      web=cloudformation.InitConfig(
          files=web.files(),
          commands=web.commands(),
          services={
              'systemd': cloudformation.InitServices(
                  {
                      'mattermost.service': cloudformation.InitService(
                          enabled=False, ensureRunning=True),
                      'nginx.service': cloudformation.InitService(
                          enabled=False, ensureRunning=True),
                  }),
          }),
  )


def launch_template(
    *,
    my_vpc,
    key_pair,
    ami,
    instance_profile,
    instance_type,
    ssh_security_group,
    web_security_group,
    instance_fingerprint,
    cfninit_log,
    mattermost_log,
    mysql_error_log,
    config_volume_value,
    db_volume_value,
    eip,
    domain,
    ebs_attach_policy,
    file_bucket,
    mail_access_key,
    email,
):
  return ec2.LaunchTemplate(
      'LaunchTemplate',
      DependsOn=ebs_attach_policy.name,
      LaunchTemplateData=ec2.LaunchTemplateData(
          BlockDeviceMappings=[
              ec2.LaunchTemplateBlockDeviceMapping(
                  DeviceName=DEVICE_ROOT_XVD,
                  Ebs=ec2.EBSBlockDevice(
                      VolumeSize=DEVICE_ROOT_SIZE, VolumeType='gp3')),
              ec2.LaunchTemplateBlockDeviceMapping(
                  DeviceName=DEVICE_SWAP_XVD,
                  Ebs=ec2.EBSBlockDevice(VolumeSize=1, VolumeType='gp3'))
          ],
          EbsOptimized=True,
          IamInstanceProfile=ec2.IamInstanceProfile(
              Arn=util.arn_of(instance_profile)),
          ImageId=util.read_param(ami),
          InstanceType=util.read_param(instance_type),
          KeyName=util.read_param(key_pair),
          NetworkInterfaces=[
              ec2.NetworkInterfaces(
                  AssociatePublicIpAddress=True,
                  DeviceIndex=0,
                  Groups=[
                      GetAtt(my_vpc, 'DefaultSecurityGroup'),
                      util.name_of(ssh_security_group),
                      util.name_of(web_security_group),
                  ]),
          ],
          # Always recreate Solo instances explicitly so as not to
          # stop the service.
          UserData=util.userdata(
              'LaunchTemplate', 'AutoScalingGroup', {
                  'fingerprint': util.read_param(instance_fingerprint),
              }),
      ),
      Metadata=ec2_metadata(
          cfninit_log=cfninit_log,
          mattermost_log=mattermost_log,
          mysql_error_log=mysql_error_log,
          config_volume_value=config_volume_value,
          db_volume_value=db_volume_value,
          eip=eip,
          domain=domain,
          file_bucket=file_bucket,
          mail_access_key=mail_access_key,
          email=email),
      TagSpecifications=[
          ec2.TagSpecifications(
              ResourceType='launch-template',
              Tags=Tags(
                  {
                      'Name': Sub('${AWS::StackName}:LaunchTemplate'),
                      'mm:stack': StackName,
                  })),
      ])
