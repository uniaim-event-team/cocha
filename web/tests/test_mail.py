import json

from chalicelib.service.athena import initialize_mail_table
from chalicelib.service.mail import process_error_mail


def test_00_initialize_mail_table() -> None:
    initialize_mail_table()


def test_sqs() -> None:
    message = '''{"notificationType": "Bounce",
     "bounce": {"feedbackId": "cf2f4f010176ae01-d495683f-d3ab-43bc-92cd-02dd909b8844-000000",
                "bounceType": "Permanent",
                "bounceSubType": "General",
                "bouncedRecipients": [{"emailAddress": "testdayo@example.com",
                                       "action": "failed",
                                       "status": "5.3.0",
                                       "diagnosticCode": "smtp; 550 <testdayo@example.com>: User unknown"}],
                "timestamp": "2021-11-06T01:55:12.000Z",
                "destination": ["testdayo@example.com"],
                "headersTruncated": false,
                "headers": [
                    {"name": "Content-Type",
                     "value": "multipart/mixed; boundary=\\"===============6055180943692849582==\\""},
                    {"name": "MIME-Version",
                     "value": "1.0"},
                    {"name": "Subject",
                     "value": "Subject..."},
                    {"name": "From",
                     "value": "from@example.com"},
                    {"name": "To",
                     "value": "testdayo@example.com"},
                    {"name": "Date",
                     "value": "Sat, 06 Nov 2021 01:55:10 -0000"}]
                },
     "mail": {"commonHeaders": {"from": ["from@example.com"],
                                "date": "Sat, 06 Nov 2021 01:55:10 -0000",
                                "to": ["testdayo@example.com"],
                                "subject": "Subject..."}}}'''
    process_error_mail(json.loads(message))
