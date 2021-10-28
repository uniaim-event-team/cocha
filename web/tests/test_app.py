import hmac
from datetime import datetime
from hashlib import sha256

from chalice.test import Client
from app import app, slack_signing_secret
from chalicelib.service.athena import get_request_distribution_graph


def test_slack_req_function() -> None:
    with Client(app) as client:
        unix_timestamp = str(int(datetime.now().timestamp()))
        sig_basestring = 'v0:' + unix_timestamp + ':text=ticket/access/0%20GET'
        slack_signature = 'v0=' + hmac.new(slack_signing_secret().encode(), sig_basestring.encode(), sha256).hexdigest()

        response = client.http.post(
            '/slack/req', body=b'text=ticket/access/0%20GET',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Slack-Request-Timestamp': unix_timestamp,
                'X-Slack-Signature': slack_signature,
            },
        )
        assert response.json_body == {
            "response_type": "in_channel",
            "text": "[req] OK, just a moment..."
        }
        # TODO check SQS queue and delete it


def test_get_request_distribution_graph() -> None:
    get_request_distribution_graph('/tp/ticket/access/0', 'GET', '')
