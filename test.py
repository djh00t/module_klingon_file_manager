from klingon_file_manager import manage_file
import base64
import hashlib
import lorem
import os
import subprocess


AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

# Set s3 bucket name
s3_bucket_name = AWS_S3_BUCKET_NAME

# Generate a 100 word string of lorem ipsum text
test_txt_content = lorem.text()

# test_txt_content = 'Hello World!'
test_bin_content = b'\x00\x00\x00\x00\x00\x00\x00\x00'

# Test Files - get
test_txt_get = 'tests/test_get_txt_file.txt'
test_bin_get = 'tests/test_get_bin_file.wav'

# Test Files - post
test_txt_post = 'tests/test_post_txt_file.txt'
test_bin_post = 'tests/test_post_bin_file.wav'

def file_size(file_content):
    return len(file_content)

# Get the file size in either bytes, kilobytes, megabytes or gigabytes depending
# on how large it is, showing up to 6 decimal places, returning a
# string
def get_file_size(file_size, show_bytes=False):
    if show_bytes:
        return f"{file_size} B"
    elif file_size < 1000000:
        return f"{round(file_size / 1000, 6)} KB"
    elif file_size < 1000000000:
        return f"{round(file_size / 1000000, 6)} MB"
    else:
        return f"{round(file_size / 1000000000, 6)} GB"

# Generate Test Binary Files
def create_test_binary_file(file_name, file_size):
    # Generate a 100MB file using dd command
    subprocess.run(
        [
            'dd',
            'if=/dev/zero',
            f'of=./{file_name}',
            'bs=1M',
            f'count={file_size}',
        ]
    )

# File Upload Function
def file_upload(action, path, content, md5=None, metadata={}, debug=False):
    # Upload the file and dump the full response from
    # klingon-file-manager to console
    result = manage_file(
        action=action,
        path=path,
        content=content,
        md5=md5,
        metadata=metadata,
        debug=debug,
    )
    print(f"Debug: {result}")
    return result

# Get MD5 hash of the generated file
def get_md5_hash(file_content):
    # Get the md5 hash of the file content
    md5_hash = hashlib.md5(file_content).digest()
    return md5_hash.hex()


def test_small_upload_progress():
    # Set test files name
    file_name = 'small_file'

    # Set file size in Mb
    create_size = '1'

    # Generate the file
    create_test_binary_file(file_name, create_size)

    # Get md5 hash of the generated file
    with open(file_name, 'rb') as f:
        # Read the file content
        file_content = f.read()

    # Get the file size in bytes
    file_size = len(file_content)

    # Create metadata dictionary
    metadata = {
        "md5": get_md5_hash(file_content),
        "filesize": file_size
    }

    # Print the file size
    print(f"File size: {get_file_size(file_size)}")

    # Upload file
    result = file_upload(
        action='post',
        path=f"s3://fsg-gobbler/tests/{file_name}",
        content=file_content,
        metadata=metadata,
        debug=False,
    )

    # Announce the upload result
    print("Upload result: ", result)




def test_medium_upload_progress():
    # Set test files name
    file_name = 'medium_file'

    # Set file size in Mb
    create_size = '10'

    # Generate the file
    create_test_binary_file(file_name, create_size)

    # Get md5 hash of the generated file
    with open(file_name, 'rb') as f:
        # Read the file content
        file_content = f.read()

    # Get the file size in bytes
    file_size = len(file_content)

    # Create metadata dictionary
    metadata = {
        "md5": get_md5_hash(file_content),
        "filesize": file_size
    }

    # Print the file size
    print(f"File size: {get_file_size(file_size)}")

    # Upload file
    result = file_upload(
        action='post',
        path=f"s3://fsg-gobbler/tests/{file_name}",
        content=file_content,
        metadata=metadata,
        debug=True,
    )

    # Announce the upload result
    print("Upload result: ", result)




def test_large_upload_progress():
    # Set test files name
    file_name = 'large_file'

    # Set file size in Mb
    create_size = '100'

    # Generate the file
    create_test_binary_file(file_name, create_size)

    # Get md5 hash of the generated file
    with open(file_name, 'rb') as f:
        # Read the file content
        file_content = f.read()

    # Get the file size in bytes
    file_size = len(file_content)

    # Create metadata dictionary
    metadata = {
        "md5": get_md5_hash(file_content),
        "filesize": file_size
    }

    # Print the file size
    print(f"File size: {get_file_size(file_size)}")

    # Upload file
    result = file_upload(
        action='post',
        path=f"s3://fsg-gobbler/tests/{file_name}",
        content=file_content,
        metadata=metadata,
        debug=False,
    )

    # Announce the upload result
    print("Upload result: ", result)

#test_small_upload_progress()
test_medium_upload_progress()
# test_large_upload_progress()
