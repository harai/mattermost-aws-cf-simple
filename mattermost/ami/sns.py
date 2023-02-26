from aws_cdk import CfnParameter
from aws_cdk.aws_sns import CfnTopic
from constructs import Construct


def notification_topic(
    scope: Construct, notification_email: CfnParameter) -> CfnTopic:
  return CfnTopic(
      scope,
      'NotificationTopic',
      subscription=[
          CfnTopic.SubscriptionProperty(
              endpoint=notification_email.value_as_string, protocol='email'),
      ])
