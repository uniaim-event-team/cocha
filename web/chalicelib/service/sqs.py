import os

from boto3.session import Session

from chalicelib.service.independent.sqs import send_message


def aws_access_key_id() -> str:
    return os.environ['ATHENA_AWS_ACCESS_KEY_ID']


def aws_secret_access_key() -> str:
    return os.environ['ATHENA_AWS_SECRET_ACCESS_KEY']


def send_sqs_message(message: str) -> None:
    # regionはchaliceと同じregionをつかう
    session = Session(
        aws_access_key_id=aws_access_key_id(), aws_secret_access_key=aws_secret_access_key())
    send_message(session, message)
