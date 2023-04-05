from mattermost.common import cfstyle
from mattermost.common.util import Imp
from mattermost.main import (
    autoscale,
    awslog,
    cloudfront,
    ec2,
    iam,
    mapping,
    parameter,
    s3,
    sns
)


def construct_template():
  t, pui = cfstyle.template('Mattermost Main')

  [
      vpc_cidr_block,
      az,
  ] = parameter.network_group(pui, t)
  [
      domain,
      hosted_zone,
      ami,
      key_pair,
      email,
      instance_type,
      instance_fingerprint,
      cloudfront_certificate_arn,
  ] = parameter.general_group(pui, t)
  [
      config_volume_stack,
      db_volume_stack,
  ] = parameter.volume_group(pui, t)
  pui.output(t)

  config_volume_imp = Imp.from_ref(config_volume_stack)
  config_volume_value = config_volume_imp.ort('ConfigVolume')

  db_volume_imp = Imp.from_ref(db_volume_stack)
  db_volume_value = db_volume_imp.ort('DbVolume')

  t.add_mapping('RegionMap', mapping.region_map())

  # VPC
  my_vpc = t.add_resource(ec2.my_vpc(vpc_cidr_block))
  subnet = t.add_resource(ec2.subnet(my_vpc, vpc_cidr_block, az))
  internet_gateway = t.add_resource(ec2.internet_gateway())
  vpc_gateway_attachment = t.add_resource(
      ec2.vpc_gateway_attachment(my_vpc, internet_gateway))
  route_table = t.add_resource(ec2.route_table(my_vpc))
  route_internet = t.add_resource(
      ec2.route_internet(
          vpc_gateway_attachment=vpc_gateway_attachment,
          route_table=route_table,
          internet_gateway=internet_gateway))
  subnet_route_table_association = t.add_resource(
      ec2.subnet_route_table_association(route_table, subnet))
  ssh_security_group = t.add_resource(ec2.ssh_security_group(my_vpc))
  web_security_group = t.add_resource(ec2.web_security_group(my_vpc))

  cfninit_log = t.add_resource(awslog.cfninit_log())
  mattermost_log = t.add_resource(awslog.mattermost_log())
  mysql_error_log = t.add_resource(awslog.mysql_error_log())

  mail_user = t.add_resource(iam.mail_user())
  mail_access_key = t.add_resource(iam.mail_access_key(mail_user))

  eip = t.add_resource(ec2.eip(my_vpc))
  file_bucket = t.add_resource(s3.file_bucket())

  ec2_instance_role = t.add_resource(
      iam.ec2_instance_role(
          cfninit_log=cfninit_log,
          mattermost_log=mattermost_log,
          mysql_error_log=mysql_error_log,
          eip=eip,
          file_bucket=file_bucket,
          domain=domain,
          hosted_zone=hosted_zone))
  instance_profile = t.add_resource(iam.instance_profile(ec2_instance_role))
  ebs_attach_policy = t.add_resource(
      iam.ebs_attach_policy(
          ec2_instance_role=ec2_instance_role,
          instance_profile=instance_profile,
          config_volume_value=config_volume_value,
          db_volume_value=db_volume_value))

  notification_topic = t.add_resource(sns.notification_topic(email))

  launch_template = t.add_resource(
      ec2.launch_template(
          my_vpc=my_vpc,
          key_pair=key_pair,
          ami=ami,
          instance_profile=instance_profile,
          instance_type=instance_type,
          ssh_security_group=ssh_security_group,
          web_security_group=web_security_group,
          instance_fingerprint=instance_fingerprint,
          cfninit_log=cfninit_log,
          mattermost_log=mattermost_log,
          mysql_error_log=mysql_error_log,
          config_volume_value=config_volume_value,
          db_volume_value=db_volume_value,
          eip=eip,
          domain=domain,
          ebs_attach_policy=ebs_attach_policy,
          file_bucket=file_bucket,
          mail_access_key=mail_access_key,
          email=email))

  t.add_resource(
      autoscale.auto_scaling_group(
          route_internet=route_internet,
          subnet_route_table_association=subnet_route_table_association,
          az=az,
          subnet=subnet,
          eip=eip,
          launch_template=launch_template,
          notification_topic=notification_topic))

  t.add_resource(
      cloudfront.distribution(
          cloudfront_certificate_arn=cloudfront_certificate_arn,
          domain=domain,
          default_cache_policy=default_cache_policy,
          distribution_log_bucket=distribution_log_bucket))

  return t


if __name__ == '__main__':
  print(construct_template().to_json(indent=2))
