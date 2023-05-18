from troposphere import StackName, Tags, sns

from mattermost.common import util


def notification_topic(email):
  return sns.Topic(
      'NotificationTopic',
      Subscription=[
          sns.Subscription(Endpoint=util.read_param(email), Protocol='email'),
      ],
      Tags=Tags({
          'mm:stack': StackName,
      }))
