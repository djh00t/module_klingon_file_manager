import os
from klingon_file_manager import manage_file
import lorem
import boto3

AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

# Set s3 bucket name
s3_bucket_name = AWS_S3_BUCKET_NAME

# Test Files - post
test_txt_post = 'tests/test_post_txt_file.txt'
test_bin_post = 'tests/test_post_bin_file.wav'

# Test 14 - delete local text files
def test_delete_local_test_txt_post_file():
    # Make sure that the test_txt_post file was created
    assert os.path.exists(test_txt_post)
    # Now, delete the local test_txt_post file
    result = manage_file('delete', test_txt_post, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_txt_post
    # Make sure that the test_txt_post file was deleted
    assert not os.path.exists(test_txt_post)

# Test 15 - delete local text files
def test_delete_local_test_txt_get_file():
    # Make sure that the test_txt_get file was created
    assert os.path.exists(test_txt_get)
    # Now, delete the local test_txt_get file
    result = manage_file('delete', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_txt_get
    # Make sure that the test_txt_get file was deleted
    assert not os.path.exists(test_txt_get)

# Test 16 - delete local binary file
def test_delete_local_test_bin_post_file():
    # Make sure that the test_bin_post file was created
    assert os.path.exists(test_bin_post)
    # Now, delete the local test_bin_post file
    result = manage_file('delete', test_bin_post, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_bin_post
    # Make sure that the test_bin_post file was deleted
    assert not os.path.exists(test_bin_post)

# Test 17 - delete local binary file
def test_delete_local_test_bin_get_file():
    # Make sure that the test_bin_get file was created
    assert os.path.exists(test_bin_get)
    # Now, delete the local test_bin_get file
    result = manage_file('delete', test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_bin_get
    # Make sure that the test_bin_get file was deleted
    assert not os.path.exists(test_bin_get)

# Test 18 - delete s3 test_txt_post file
def test_delete_s3_test_txt_post_file():
    # Now, delete the s3 text file
    result = manage_file('delete', f"s3://{s3_bucket_name}/{test_txt_post}", None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_txt_post}"

# Test 19 - delete s3 test_bin_post file
def test_delete_s3_test_bin_post_file():
    # Now, delete the s3 test_bin_post file
    result = manage_file('delete', f"s3://{s3_bucket_name}/{test_bin_post}", None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_bin_post}"

# Test 20 - delete s3 test_txt_get file
def test_delete_s3_test_txt_get_file():
    # Now, delete the s3 test_txt_get file
    result = manage_file('delete', f"s3://{s3_bucket_name}/{test_txt_get}", None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_txt_get}"
    
# Test 21 - delete s3 test_bin_get file
def test_delete_s3_test_bin_get_file():
    # Now, delete the s3 test_bin_get file
    result = manage_file('delete', f"s3://{s3_bucket_name}/{test_bin_get}", None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_bin_get}"
