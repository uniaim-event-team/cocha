from chalice.test import Client
from app import app


def test_req_function() -> None:
    with Client(app) as client:
        response = client.http.get('/req?p=dummy&m=POST')
        assert response.json_body == {'hello': 'world'}
        # TODO check SQS queue and delete it


def test_slack_req_function() -> None:
    with Client(app) as client:
        response = client.http.post(
            '/slack/req', body=b'text=ticket/access/0%20GET',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        assert response.json_body == {
            "response_type": "in_channel",
            "text": "OK, just a moment..."
        }
        # TODO check SQS queue and delete it
