from troposphere import sns

from mattermost.common import util


def notification_topic(notification_email):
  return sns.Topic(
      'NotificationTopic',
      Subscription=[
          sns.Subscription(
              Endpoint=util.read_param(notification_email), Protocol='email'),
      ])
