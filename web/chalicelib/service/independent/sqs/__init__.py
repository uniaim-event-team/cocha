import os

from boto3 import Session


def queue_url() -> str:
    return os.environ['ATHENA_SQS_URL']


def send_message(session: Session, message: str) -> None:
    sqs = session.client('sqs')
    sqs.send_message(QueueUrl=queue_url(), MessageBody=message)
