from boto3.session import Session


def output_bytes_as_file(session: Session, binary: bytes, bucket: str, file_name: str) -> None:
    s3 = session.client('s3')
    s3.put_object(Body=binary, Bucket=bucket, Key=file_name)
