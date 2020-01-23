import boto3
import pprint
import json
import logging
from os import environ as env
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# lambda env Variables
SLACK_CHANNEL = env['slackChannel']
HOOK_URL = env['slackHookURL']
HTTPS_ENDPOINT = env['httpEndPoint']
CLUSTER_NAME = env['clusterName']
RUNBOOK = env['runbook']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: %s", json.dumps(event, indent=4))
    status_info = event['detail']
    logger.info("Event: %s", json.dumps(event, indent=4))
    alert_title = event['detail']['eventDescription'][0]['latestDescription']
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(
        InstanceIds = [event['resources'][0]]
    )

    instanceTags = response['Reservations'][0]['Instances'][0]['Tags']

    for i in range(0, len(response['Reservations'][0]['Instances'][0]['Tags'])):
        key = response['Reservations'][0]['Instances'][0]['Tags'][i]['Key']
        if key == 'KubernetesCluster':
            cluster = response['Reservations'][0]['Instances'][0]['Tags'][i]['Value']
            pprint.pprint(cluster)
            # pprint.pprint(i)

    pprint.pprint(cluster)
    pprint.pprint(env['clusterName'])

    if env['clusterName'] == cluster:
        # TODO: write code...
        text = (
            f"EC2 instance {event['resources']} in {event['region']}"
            f" belongs to account {event['account']}"
            f" is scheduled for retirement on {status_info['startTime']}"
            f" instance belongs to cluster {cluster} and has tags:{instanceTags} "
        )

        slack_message = {'channel': SLACK_CHANNEL, 'text': text}
        req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))
        try:
            response = urlopen(req)
            response.read()
            logger.info("Message posted to %s", slack_message['channel'])
        except HTTPError as e:
            logger.error("Request failed: %d %s", e.code, e.reason)
        except URLError as e:
            logger.error("Server Connection failed:  %s", e.reason)

        https_message = {
            'title': alert_title,
            'channel': SLACK_CHANNEL,
            'accountName': event['account'],
            'AWSregion': event['region'],
            'alertName': event['detail-type'],
            'instanceName': event['resources'],
            'AlertDescription': text,
            'info': status_info['eventDescription'],
            'support': "devops",
            'tags': status_info['affectedEntities'],
            'instanceTags': instanceTags,
            'Runbook': RUNBOOK
        }
        req1 = Request(HTTPS_ENDPOINT, json.dumps(https_message).encode('utf-8'))
        try:
            response = urlopen(req1)
            response.read()
            logger.info("Message posted to %s", https_message['channel'])
        except HTTPError as e:
            logger.error("Request failed: %d %s", e.code, e.reason)
        except URLError as e:
            logger.error("Server connection failed: %s", e.reason)

    else:
        text = (
            f"Instance {event['resources']} doesn't belong to this {cluster} cluster "
        )
        print(text)
