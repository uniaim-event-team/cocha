from datetime import datetime
from typing import NamedTuple, Any, Dict

from boto3 import Session

from chalicelib.environment import read_environ_var
from chalicelib.service.independent.s3 import output_bytes_as_file
from chalicelib.service.independent.slack import post_text_to_slack


channel = read_environ_var('SLACK_CHANNEL')
aws_access_key_id = read_environ_var('ATHENA_AWS_ACCESS_KEY_ID')
aws_secret_access_key = read_environ_var('ATHENA_AWS_SECRET_ACCESS_KEY')
mail_bucket = read_environ_var('S3_MAIL_BUCKET')


class ErrorMail(NamedTuple):
    email_address: str
    diagnostic_code: str
    status: str


def process_error_mail(result: Dict[str, Any]) -> None:
    notification_type = result['notificationType']
    error_mail = []
    subject = result['mail']['commonHeaders']['subject'].replace(',', '')
    if notification_type == 'Bounce':
        for recipients in result['bounce']['bouncedRecipients']:
            error_mail.append(ErrorMail(
                email_address=recipients['emailAddress'],
                diagnostic_code=recipients['diagnosticCode'],
                status=recipients['status'],
            ))
    elif notification_type == 'Complaint':
        for recipients in result['complaint']['complainedRecipients']:
            error_mail.append(ErrorMail(
                email_address=recipients['emailAddress'],
                diagnostic_code='',
                status='',
            ))
    output_str = 'notification_type,subject,email_address,diagnostic_code,status\n'
    for email_address, diagnostic_code, status in error_mail:
        output_str += f'{notification_type},{subject},{email_address},{diagnostic_code},{status}\n'

    session = Session(
        aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    output_bytes_as_file(session, output_str.encode(), mail_bucket, datetime.now().strftime('%Y/%m/%d/%Y%m%d%H%M%S%f'))

    post_text_to_slack(
        channel, f'[ErrorMail]{",".join([b.email_address for b in error_mail])}')
