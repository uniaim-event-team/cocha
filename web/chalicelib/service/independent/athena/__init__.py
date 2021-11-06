from datetime import datetime
import time
from typing import Optional

from boto3.session import Session
from mypy_boto3_athena.type_defs import GetQueryExecutionOutputTypeDef

from chalicelib.environment import read_environ_var

athena_database = read_environ_var('ATHENA_DATABASE')
log_table_prefix = read_environ_var('LOG_TABLE_PREFIX')
s3_result_folder = read_environ_var('S3_RESULT_FOLDER')
s3_result_bucket = s3_result_folder.split('/')[0]
s3_result_sub_folder = s3_result_folder[len(s3_result_bucket) + 1:]
s3_mail_bucket = read_environ_var('S3_MAIL_BUCKET')


def execute_query(session: Session, query: str) -> str:
    athena = session.client('athena')
    start_result = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': athena_database
        },
        ResultConfiguration={
            'OutputLocation': 's3://' + s3_result_folder
        }
    )
    return start_result['QueryExecutionId']


def get_query_result(session: Session, query_execution_id: str, store_file_name: str) -> None:
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
        raise Exception('No results')

    status = result['QueryExecution']['Status']['State']
    if status == 'SUCCEEDED':
        output_location = result['QueryExecution']['ResultConfiguration']['OutputLocation']
        file_name = output_location.split('/')[-1]
        s3 = session.client('s3')
        s3.download_file(s3_result_bucket, s3_result_sub_folder + file_name, store_file_name)
    else:
        raise Exception(str(result))


def begin_request_distribution_query(session: Session, url_like: str, method: str) -> str:
    query = f'''
    select
        time,
        target_processing_time,
        elb_status_code
    from {log_table_prefix}{datetime.now().strftime("%Y%m")}
    where request_url like '%{url_like}%'
    and request_verb = '{method}'
    order by time
    '''
    return execute_query(session, query)


def get_failed_mail_query(session: Session, subject_like: str) -> str:
    query = f'''
    select
        notification_type,
        subject,
        email_address,
        diagnostic_code,
        status
    from mail_logs
    where subject like '%{subject_like}%'
    '''
    return execute_query(session, query)


def create_table_mail(session: Session) -> str:
    query = f'''
CREATE EXTERNAL TABLE IF NOT EXISTS `mail_logs`(
    `notification_type` string COMMENT '',
    `subject` string COMMENT '',
    `email_address` string COMMENT '',
    `diagnostic_code` string COMMENT '',
    `status` string COMMENT '')
ROW FORMAT SERDE
  'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
  'input.regex'='([^,]*),([^,]*),([^,]*),([^,]*),([^,]*)')
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://{s3_mail_bucket}/'
    '''
    return execute_query(session, query)
