import boto3
import os
import tiktoken
import json
from openai import OpenAI
from botocore.exceptions import ClientError
from pathlib import Path
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 80
TEXT_EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_ROOT_KEY = "chunks"
tokenizer = tiktoken.get_encoding("cl100k_base")
s3_client = boto3.client('s3')


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
    
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)



def split_text_into_chunks_with_overlap(text):
    tokens = tokenizer.encode(text)  # Tokenize the input text
    chunks = []
    # Loop through the tokens, creating chunks with overlap
    for i in range(0, len(tokens), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk_tokens = tokens[i:i + CHUNK_SIZE]  # Include overlap by adjusting start point
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks

def get_embedding(text, model=TEXT_EMBEDDING_MODEL):
    return openai_client.embeddings.create(input = [text], model=model).data[0].embedding



def lambda_handler(event, context):
    # Get bucket name and object key from the S3 event
    bucket_name = os.environ['BUCKET_NAME']
    file_key = event['Records'][0]['s3']['object']['key']

    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    text = response['Body'].read().decode('utf-8')
    
    # Split the text into chunks
    chunks = split_text_into_chunks_with_overlap(text)
    
    # Calculate embeddings 
    embeddings = []
    for idx, chunk in enumerate(chunks):
        # get embedding of chunk
        embedding = get_embedding(chunk)
        embeddings.append(embedding)

        file_key_name = Path(file_key).stem # the document filename without extension
        body = {
            "text": chunk,
            "embedding": embedding,
            "idx": idx,
            "filename": file_key_name
        }
        # Save embeddings back to S3
        save_key = CHUNK_ROOT_KEY + "/" + file_key_name + "/" + f"{idx}.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=save_key,
            Body=json.dumps(body)
        )
    logger.info(f"Embeddings saved to S3 for file {file_key_name}, under {bucket_name}/{save_key}")
    return {
        'statusCode': 200,
        'body': json.dumps('Files processed and embedding saved!')
    }