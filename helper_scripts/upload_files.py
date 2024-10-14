"""
File to upload files to s3 bucket
"""


import boto3
import os
from botocore.exceptions import NoCredentialsError
from tqdm.auto import tqdm

S3_BUCKET_NAME = "information-bucket-1231230123"
S3_BUCKET_REGION = "eu-north-1"

# Define the bucket name and the folder containing your text files
folder = r'C:\Users\eivin\Documents\Programming\LovAvgjørelser\Data\hoyesteretts_dommer\extracted_info_pages'

bucket_prefix = "texts"

s3_client = boto3.client('s3')


def upload_file(file_path):
	# s3_client.upload_file(file_path, S3_BUCKET_NAME, file_path)
	s3_client.upload_file(file_path, S3_BUCKET_NAME, f'{bucket_prefix}/{os.path.basename(file_path)}')
	print(f'Uploaded {file_path} to bucket: {S3_BUCKET_NAME}')

def is_from_year_and_later(chunk, year):
	for _ in range(100):
		if year in chunk:
			return True
		year = str(int(year)+1)
	return False

MINIMUM_YEAR = "2019"
all_filenames = os.listdir(folder)
filtered_filenames = [filename for filename in tqdm(all_filenames) if is_from_year_and_later(filename, MINIMUM_YEAR)] 
# TODO upload with test first

# for idx, filename in tqdm(enumerate(os.listdir(folder))):
for idx, filename in tqdm(enumerate(filtered_filenames)):

	file_path = os.path.join(folder, filename)
	upload_file(file_path)