import os
from datetime import datetime
import time
from typing import Optional

from boto3.session import Session
from mypy_boto3_athena.type_defs import GetQueryExecutionOutputTypeDef


def athena_database() -> str:
    return os.environ['ATHENA_DATABASE']


def log_table_prefix() -> str:
    return os.environ['LOG_TABLE_PREFIX']


def s3_result_folder() -> str:
    return os.environ['S3_RESULT_FOLDER']


def s3_result_bucket() -> str:
    return s3_result_folder().split('/')[0]


def s3_result_sub_folder() -> str:
    return s3_result_folder()[len(s3_result_bucket()) + 1:]


def begin_request_distribution_query(session: Session, url_like: str, method: str) -> str:
    athena = session.client('athena')
    athena_query = f'''
    select
        time,
        target_processing_time,
        elb_status_code
    from {log_table_prefix()}{datetime.now().strftime("%Y%m")}
    where request_url like '%{url_like}%'
    and request_verb = '{method}'
    order by time
    '''

    start_result = athena.start_query_execution(
        QueryString=athena_query,
        QueryExecutionContext={
            'Database': athena_database()
        },
        ResultConfiguration={
            'OutputLocation': 's3://' + s3_result_folder()
        }
    )
    return start_result['QueryExecutionId']


def get_query_result(session: Session, query_execution_id: str, store_file_name: str) -> str:
    athena = session.client('athena')
    result: Optional[GetQueryExecutionOutputTypeDef] = None
    for sec in range(100):
        print(f'{sec}sec...')
        result = athena.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        if 'Status' in result['QueryExecution'] and \
                result['QueryExecution']['Status'].get('State', 'QUEUED') not in ('QUEUED', 'RUNNING'):
            break
        time.sleep(1)

    if not result:
        return ''

    status = result['QueryExecution']['Status']['State']
    if status == 'SUCCEEDED':
        output_location = result['QueryExecution']['ResultConfiguration']['OutputLocation']
        file_name = output_location.split('/')[-1]
        s3 = session.client('s3')
        s3.download_file(s3_result_bucket(), s3_result_sub_folder() + file_name, store_file_name)

    return status
