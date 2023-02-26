from mattermost.ami import iam, imagebuilder, parameter, s3, sns
from mattermost.common.template import Template


class AmiTemplate(Template):

  name: str = 'Mattermost AMI'

  def definition(self) -> None:
    base_ami = parameter.base_ami(self)
    key_pair = parameter.key_pair(self)
    notification_email = parameter.notification_email(self)

    log_bucket = s3.log_bucket(self)
    notification_topic = sns.notification_topic(self, notification_email)
    builder_instance_role = iam.builder_instance_role(self, log_bucket)
    builder_instance_profile = iam.builder_instance_profile(
        self, builder_instance_role)
    infrastructure_configuration = imagebuilder.infrastructure_configuration(
        self, builder_instance_profile, key_pair, log_bucket,
        notification_topic)

    component = imagebuilder.component(self)
    image_recipe = imagebuilder.image_recipe(self, base_ami, component)
    imagebuilder.image_pipeline(
        self, image_recipe, infrastructure_configuration)
