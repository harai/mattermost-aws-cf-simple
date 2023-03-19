from mattermost.ami import awslog, ec2, iam, imagebuilder, parameter, s3, sns
from mattermost.common import cfstyle


def construct_template():
  t, pui = cfstyle.template('Mattermost AMI')

  [
      vpc_cidr_block,
      az,
  ] = parameter.network_group(pui, t)
  [
      base_ami,
      key_pair,
      notification_email,
      mattermost_version,
  ] = parameter.general_group(pui, t)
  pui.output(t)

  # VPC
  my_vpc = t.add_resource(ec2.my_vpc(vpc_cidr_block))
  subnet = t.add_resource(ec2.subnet(my_vpc, vpc_cidr_block, az))
  internet_gateway = t.add_resource(ec2.internet_gateway())
  vpc_gateway_attachment = t.add_resource(
      ec2.vpc_gateway_attachment(my_vpc, internet_gateway))
  route_table = t.add_resource(ec2.route_table(my_vpc))
  route_internet = t.add_resource(
      ec2.route_internet(vpc_gateway_attachment, route_table, internet_gateway))
  subnet_route_table_association = t.add_resource(
      ec2.subnet_route_table_association(route_table, subnet))
  ssh_security_group = t.add_resource(ec2.ssh_security_group(my_vpc))

  builder_log = t.add_resource(awslog.builder_log())
  log_bucket = t.add_resource(s3.log_bucket())
  notification_topic = t.add_resource(
      sns.notification_topic(notification_email))
  builder_instance_role = t.add_resource(
      iam.builder_instance_role(log_bucket, builder_log))
  builder_instance_profile = t.add_resource(
      iam.builder_instance_profile(builder_instance_role))
  infrastructure_configuration = t.add_resource(
      imagebuilder.infrastructure_configuration(
          builder_instance_profile=builder_instance_profile,
          key_pair=key_pair,
          log_bucket=log_bucket,
          notification_topic=notification_topic,
          my_vpc=my_vpc,
          subnet=subnet,
          route_internet=route_internet,
          subnet_route_table_association=subnet_route_table_association,
          ssh_security_group=ssh_security_group))

  component = t.add_resource(imagebuilder.component())
  image_recipe = t.add_resource(
      imagebuilder.image_recipe(base_ami, component, mattermost_version))
  t.add_resource(
      imagebuilder.image_pipeline(image_recipe, infrastructure_configuration))

  return t


if __name__ == '__main__':
  print(construct_template().to_json(indent=2))
