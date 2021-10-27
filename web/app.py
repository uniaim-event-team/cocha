import json
import os
import urllib.parse
from typing import Dict

from chalice.app import Chalice, SQSEvent

from chalicelib.service.athena import get_request_distribution_graph
from chalicelib.service.independent.slack import post_text_to_slack
from chalicelib.service.sqs import send_sqs_message

app = Chalice(app_name='web')


if 'ATHENA_SQS_URL' not in os.environ:
    with open('.chalice/config.json') as f:
        sqs_queue = json.load(f)['environment_variables']['ATHENA_SQS_URL'].split('/')[-1]
else:
    sqs_queue = os.environ['ATHENA_SQS_URL'].split('/')[-1]


def channel() -> str:
    return os.environ['SLACK_CHANNEL']


@app.route('/req')
def req() -> Dict[str, str]:
    request = app.current_request
    message = request.path + '?' + urllib.parse.urlencode(request.query_params or {})
    send_sqs_message(message)
    return {'hello': 'world'}


@app.route('/slack/req', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def slack_req() -> Dict[str, str]:
    request = app.current_request
    message = request.path + '?' + (request.raw_body or b'').decode()
    send_sqs_message(message)
    return {
        "response_type": "in_channel",
        "text": "OK, just a moment..."
    }


@app.on_sqs_message(queue=sqs_queue)
def handle_sqs_message(event: SQSEvent) -> None:
    for record in event:
        slack_channel = ''
        try:
            parsed_result = urllib.parse.urlparse(urllib.parse.unquote(record.body))
            query = {k: v for k, v in urllib.parse.parse_qsl(parsed_result.query)}
            if parsed_result.path == '/req':
                get_request_distribution_graph(query.get('p', ''), query.get('m', ''), '')
            if parsed_result.path == '/slack/req':
                slack_channel = query.get('channel_id', '')
                command_input = query.get('text', '').split(' ')
                get_request_distribution_graph(command_input[0], command_input[1], slack_channel)
        except Exception:
            post_text_to_slack(slack_channel or channel(), 'Nadie te quiere.')


@app.route('/slack/lgtm', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def slack_lgtm() -> Dict[str, str]:
    """
    BOT機能（おまけ）
    :return:
    """
    request = app.current_request
    query = {k: v for k, v in urllib.parse.parse_qsl((request.raw_body or b'').decode())}
    command_input = query.get('text', '').split(' ')
    if command_input[0] == 'all':
        return {
            "response_type": "in_channel",
            "text": "<!channel> やあ、みんな！進捗はどうだい？困ったことがあったら相談してね！"
        }
    if command_input[0] == 'lgtm':
        some_good_message = 'LGTM!'
        return {
            "response_type": "in_channel",
            "text": f"<@{query.get('user_id')}> " + some_good_message
        }
    if command_input[0] == 'help':
        return {
            "response_type": "in_channel",
            "text": "このアプリはChatOpsを推進するためにChaliceで作ったアプリだよ〜\n"
                    "/lgtm all\n"
                    "みんなの進捗を確認するよ〜\n"
                    "/lgtm lgtm\n"
                    "承認欲求を満たすよ〜\n"
                    "/lgtm help\n"
                    "使い方を説明するよ〜\n"
        }
    return {
        "response_type": "in_channel",
        "text": "Nadie te quiere."
    }
