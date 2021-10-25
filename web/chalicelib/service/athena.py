import os
import tempfile

from boto3.session import Session

from chalicelib.service.independent.athena import begin_request_distribution_query, get_query_result
from chalicelib.service.independent.plot import plot_histogram
from chalicelib.service.independent.slack import post_image_to_slack


def channel() -> str:
    return os.environ['SLACK_CHANNEL']


def aws_access_key_id() -> str:
    return os.environ['ATHENA_AWS_ACCESS_KEY_ID']


def aws_secret_access_key() -> str:
    return os.environ['ATHENA_AWS_SECRET_ACCESS_KEY']


def get_request_distribution_graph(url_like: str, method: str, slack_channel: str) -> None:
    # regionはchaliceと同じregionをつかう
    session = Session(
        aws_access_key_id=aws_access_key_id(), aws_secret_access_key=aws_secret_access_key())
    query_execution_id = begin_request_distribution_query(session, url_like)
    input_temp = tempfile.NamedTemporaryFile()
    status = get_query_result(session, query_execution_id, input_temp.name)
    if status == 'SUCCEEDED':
        output_temp = tempfile.NamedTemporaryFile()
        plot_histogram(input_temp.name, url_like, method, output_temp)
        post_image_to_slack(slack_channel or channel(), output_temp)
