import hmac
import json
import traceback
import urllib.parse
from datetime import datetime
from functools import wraps
from hashlib import sha256
from typing import Dict, Any

from chalice.app import Chalice, SQSEvent

from chalicelib.environment import read_environ_var
from chalicelib.service.independent.slack import post_text_to_slack
from chalicelib.service.mail import process_error_mail
from chalicelib.service.sqs import send_sqs_message

app = Chalice(app_name='web')


athena_queue_url = read_environ_var('ATHENA_SQS_URL')
athena_queue = athena_queue_url.split('/')[-1]
mail_queue_url = read_environ_var('MAIL_SQS_URL')
mail_queue = mail_queue_url.split('/')[-1]
channel = read_environ_var('SLACK_CHANNEL')
slack_signing_secret = read_environ_var('SLACK_SIGNING_SECRET')


def validate_slack_post(f: Any) -> Any:

    @wraps(f)
    def deco_func(*args: Any, **kwargs: Any) -> Any:
        request = app.current_request
        unix_timestamp = request.headers['X-Slack-Request-Timestamp']
        if datetime.now().timestamp() - int(unix_timestamp) > 60 * 5:
            return {
                "response_type": "in_channel",
                "text": "[Error] Too old."
            }

        sig_basestring = 'v0:' + unix_timestamp + ':' + (request.raw_body or b'').decode()
        my_signature = 'v0=' + hmac.new(slack_signing_secret.encode(), sig_basestring.encode(), sha256).hexdigest()
        slack_signature = request.headers['X-Slack-Signature']
        if my_signature != slack_signature:
            return {
                "response_type": "in_channel",
                "text": "[Error] Wrong signature."
            }

        return f(*args, **kwargs)

    return deco_func


@app.route('/slack/{path}', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
@validate_slack_post
def slack_req(path: str) -> Dict[str, str]:
    request = app.current_request
    message = '/slack/' + path + '?' + (request.raw_body or b'').decode()
    send_sqs_message(read_environ_var('ATHENA_SQS_URL'), message)
    return {
        "response_type": "in_channel",
        "text": f"[{path}] OK, just a moment..."
    }


@app.on_sqs_message(queue=athena_queue)
def handle_sqs_message(event: SQSEvent) -> None:
    for record in event:
        slack_channel = ''
        try:
            parsed_result = urllib.parse.urlparse(urllib.parse.unquote(record.body))
            query = {k: v for k, v in urllib.parse.parse_qsl(parsed_result.query)}
            if parsed_result.path == '/slack/req':
                from chalicelib.service.athena import get_request_distribution_graph
                slack_channel = query.get('channel_id', '')
                command_input = query.get('text', '').split(' ')
                get_request_distribution_graph(command_input[0], command_input[1], slack_channel)
        except Exception as ex:
            post_text_to_slack(slack_channel or channel, 'Nadie te quiere.' + str(ex) + traceback.format_exc())


@app.on_sqs_message(queue=mail_queue)
def handle_error_mail(event: SQSEvent) -> None:
    for record in event:
        try:
            process_error_mail(json.loads(record.body))
        except Exception as ex:
            post_text_to_slack(
                channel, '[Mail] Nadie te quiere.' + str(ex) + traceback.format_exc())


@app.route('/slack/lgtm', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
@validate_slack_post
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
        "text": "Nadie te quiere!"
    }
