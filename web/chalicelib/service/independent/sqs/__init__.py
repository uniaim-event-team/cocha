from boto3.session import Session


def send_message(session: Session, queue_url: str, message: str) -> None:
    sqs = session.client('sqs')
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)
