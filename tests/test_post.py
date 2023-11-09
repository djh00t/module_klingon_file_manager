import os
from klingon_file_manager import manage_file
import lorem
import boto3

AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

# Set s3 bucket name
s3_bucket_name = AWS_S3_BUCKET_NAME

# Generate a 100 word string of lorem ipsum text
test_txt_content = lorem.text()
test_bin_content = b'\x00\x00\x00\x00\x00\x00\x00\x00'

# Test Files - post
test_txt_post = 'tests/test_post_txt_file.txt'
test_bin_post = 'tests/test_post_bin_file.wav'

# Test 5 - post local text file
def test_post_local_txt_file():
    result = manage_file('post', test_txt_post, test_txt_content)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['content'] == test_txt_content
    assert result['path'] == test_txt_post
    assert result['binary'] is False

# Test 6 - post local binary file
def test_post_local_bin_file():
    result = manage_file('post', test_bin_post, test_bin_content)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['content'] == test_bin_content
    assert result['path'] == test_bin_post
    assert result['binary'] is True

# Test 7 - post s3 text file
def test_post_s3_txt_file():
    result = manage_file(
        'post', f"s3://{s3_bucket_name}/{test_txt_post}", test_txt_content
    )
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_txt_post}"
    assert result['binary'] is False
    # Additional check: Read the file from s3 to make sure content was written
    # correctly
    validate = manage_file('get', f"s3://{s3_bucket_name}/{test_txt_post}", None)
    print(validate)
    assert validate['status'] == 200
    assert validate['action'] == 'get'
    assert validate['content'].decode() == test_txt_content
    assert validate['path'] == f"s3://{s3_bucket_name}/{test_txt_post}"

# Test 8 - post s3 binary file
def test_post_s3_bin_file():
    result = manage_file(
        'post', f"s3://{s3_bucket_name}/{test_bin_post}", test_bin_content
    )
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_bin_post}"
    # Additional check: Read the file from s3 to make sure content was written
    # correctly
    validate = manage_file('get', f"s3://{s3_bucket_name}/{test_bin_post}", None)
    print(validate)
    assert validate['status'] == 200
    assert validate['action'] == 'get'
    assert validate['content'] == test_bin_content
    assert validate['path'] == f"s3://{s3_bucket_name}/{test_bin_post}"
