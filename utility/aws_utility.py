import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name = "OPENAI_API_KEY", region_name = "eu-north-1"):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )["SecretString"]
        # convert to dict
        secret_value_response = eval(secret_value_response)[secret_name]
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    return secret_value_response
    

