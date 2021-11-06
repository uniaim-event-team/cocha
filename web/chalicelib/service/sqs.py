from boto3.session import Session

from chalicelib.environment import read_environ_var
from chalicelib.service.independent.sqs import send_message


aws_access_key_id = read_environ_var('ATHENA_AWS_ACCESS_KEY_ID')
aws_secret_access_key = read_environ_var('ATHENA_AWS_SECRET_ACCESS_KEY')


def send_sqs_message(queue_url: str, message: str) -> None:
    # regionはchaliceと同じregionをつかう
    session = Session(
        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    send_message(session, queue_url, message)
