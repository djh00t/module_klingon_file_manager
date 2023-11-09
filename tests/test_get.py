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

# Test Files - get
test_txt_get = 'tests/test_get_txt_file.txt'
test_bin_get = 'tests/test_get_bin_file.wav'

def compare_s3_local_file(local_file, s3_file):
    # Download the S3 file to a tmp file name
    s3 = boto3.resource('s3')
    s3.meta.client.download_file(s3_bucket_name, s3_file, 'tests/tmp')
    # Make sure that the tmp file was created
    assert os.path.exists('tests/tmp')
    # Compare the local file to the tmp file
    local_file_content = open(local_file, 'rb').read()
    tmp_file_content = open('tests/tmp', 'rb').read()
    # Make sure that the local file and the tmp file have the same content
    assert local_file_content == tmp_file_content
    # Delete the tmp file
    os.remove('tests/tmp')

# Test 1 - get local text file
def test_get_local_txt_file():
    result = manage_file('get', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'].decode() == test_txt_content
    assert result['path'] == test_txt_get
    assert result['binary'] is False
    # Additional check: Read the file to make sure content was written
    # correctly
    with open(test_txt_get, 'r') as file:
        assert file.read() == test_txt_content

# Test 2 - get local binary file
def test_get_local_bin_file():
    result = manage_file('get', test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'] == test_bin_content
    assert result['path'] == test_bin_get
    assert result['binary'] is True
    # Additional check: Read the file to make sure content was written
    # correctly
    with open(test_bin_get, 'rb') as file:
        assert file.read() == test_bin_content

# Test 3 - get s3 text file
def test_get_s3_txt_file():
    result = manage_file('get', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'].decode() == test_txt_content
    assert result['path'] == test_txt_get
    assert result['binary'] is False

# Test 4 - get s3 binary file
def test_get_s3_bin_file():
    result = manage_file('get', test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'] == test_bin_content
    assert result['path'] == test_bin_get
    assert result['binary'] is True

# Test 10 - Test invalid local path
def test_get_invalid_local_path():
    result = manage_file('get', './nonexistent.txt' , None)
    print(result)
    assert result['status'] == 500
    assert result['action'] == 'get'

# Test 11 - Test invalid S3 path
def test_get_invalid_s3_path():
    result = manage_file('get', f's3://{s3_bucket_name}/nonexistent.txt', None)
    print(result)
    assert result['status'] == 500
    assert result['action'] == 'get'
# Test 1 - get local text file
def test_get_local_txt_file():
    result = manage_file('get', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'].decode() == test_txt_content
    assert result['path'] == test_txt_get
    assert result['binary'] is False
    # Additional check: Read the file to make sure content was written
    # correctly
    with open(test_txt_get, 'r') as file:
        assert file.read() == test_txt_content
