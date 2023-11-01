# utils.py
"""
# Utils Overview
Utility functions for the Klingon File Manager, including AWS credential fetching.

This module provides a centralized way to manage file operations on both
local and AWS S3 storage. It leverages utility functions from the `utils` module
and specific actions from `get`, `post`, and `delete` modules.

# Functions

## get_mime_type
Fetch the MIME type of a file.

## get_aws_credentials
Fetch AWS credentials.

## is_binary_file
Check if a file is binary.

# Usage Examples

To get the MIME type of a local file:
```python
>>> get_mime_type('/path/to/local/file.txt')
'text/plain'
```

To get the MIME type of an S3 file:
```python
>>> get_mime_type('s3://bucket/file.jpg')
'image/jpeg'
```

To check if a local file is binary:
```python
>>> is_binary_file('/path/to/local/file.bin')
True
```

To check if an S3 file is binary:
```python
>>> is_binary_file('s3://bucket/file.bin')
True
```

To fetch AWS credentials:
```python
>>> credentials = get_aws_credentials()
>>> print(credentials['aws_access_key_id'])
{
    'status': 200,
    'message': 'AWS credentials retrieved successfully.',
    'credentials': {
        'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    }
}
```
"""

from boto3 import Session
from dotenv import load_dotenv
from typing import Dict, Union
import boto3
import botocore.exceptions
import magic
import os


def get_mime_type(file_path: str) -> str:
    """
    # Get the MIME type of a file

    ## Args
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | file_path | string            | Path to the file |   |

    ## Returns
    A string containing the MIME type of the file. For example if run against a
    jpeg file, the function would return `image/jpeg`
    
    """
    if file_path.startswith('s3://'):
        s3 = boto3.client('s3')
        bucket_name, key = file_path[5:].split('/', 1)
        obj = s3.get_object(Bucket=bucket_name, Key=key)
        return obj['ContentType']
    else:
        with open(file_path, 'rb') as file:
            content = file.read()
        return magic.from_buffer(content, mime=True)




def check_bucket_permissions(bucket_name, s3):
    permissions = {
        'ListBucket': False,
        'GetBucketAcl': False,
        'PutObject': False,
        'DeleteObject': False,
    }

    try:
        s3.list_objects_v2(Bucket=bucket_name, MaxKeys=0)
        permissions['ListBucket'] = True
    except:
        pass

    try:
        s3.get_bucket_acl(Bucket=bucket_name)
        permissions['GetBucketAcl'] = True
    except:
        pass

    try:
        object_key = 'temp_permission_check_object'
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=b'')
        permissions['PutObject'] = True
        s3.delete_object(Bucket=bucket_name, Key=object_key)
        permissions['DeleteObject'] = True
    except:
        pass

    return permissions

def get_aws_credentials(debug: bool = False) -> Dict[str, Union[int, str]]:
    """
    # Get AWS credentials and check access to S3 buckets
    
    Fetches AWS credentials from .env file or environment variables. If the
    function finds them, it checks if they are valid and returns them along
    with a list of buckets and the permissions the credentials have to each.

    ## Args
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | debug     | bool              | Flag to enable debugging. | False |

    ## Returns
    A dictionary containing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY as well
    as a list of buckets the credentials have read and write access to as follows:

    ```python
    {
        'status': 200,
        'message': 'AWS credentials retrieved successfully.',
        'credentials': {
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        },
        'access': {
                'bucket1': {
                    'ListBucket': true,
                    'GetBucketAcl': true,
                    'PutObject': true,
                    'DeleteObject': true
                },
                'bucket2': {
                    'ListBucket': true,
                    'GetBucketAcl': true,
                    'PutObject': true,
                    'DeleteObject': true
                }
        },
    }
    ```
    """
    load_dotenv()
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Make sure there are AWS variables in the dotenv or environment
    if not access_key or not secret_key:
        return {
            'status': 424,
            'message': 'Failed Dependency - No working AWS credentials in .env or environment',
        }

    # Check if the credentials are valid and user can login
    session = Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    try:
        user = session.client('iam').get_user()
    except Exception as e:
        return {
            'status': 403,
            'message': 'Access Denied - AWS credentials are invalid',
        }

    # Check if the credentials have read and write access to any s3 buckets
    s3 = session.client('s3')
    response = s3.list_buckets()
    buckets = response['Buckets']

    access = {}
    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            s3.head_bucket(Bucket=bucket_name)
            permissions = check_bucket_permissions(bucket_name, s3)
            access[bucket_name] = permissions
        except:
            pass

    return {
        'status': 200,
        'message': 'AWS credentials retrieved successfully.',
        'credentials': {
            'AWS_ACCESS_KEY_ID': access_key,
            'AWS_SECRET_ACCESS_KEY': secret_key,
        },
        'access': access
    }

def is_binary_file(file_path_or_content: Union[str, bytes]) -> bool:
    """
    # Check if a file or content is binary

    ## Args
    | Name      | Type              | Description |
    |-----------|-------------------|-------------|
    | file_path_or_content | string or bytes | The path to the file or the content of the file. |

    ## Returns
    A boolean value of true if the file or content is binary, False otherwise.
    """
    if isinstance(file_path_or_content, str):
        if file_path_or_content.startswith('s3://'):
            s3 = boto3.client('s3')
            bucket_name, key = file_path_or_content[5:].split('/', 1)
            obj = s3.get_object(Bucket=bucket_name, Key=key)
            return obj['ContentType'].startswith('application/')
        else:
            with open(file_path_or_content, 'rb') as file:
                content = file.read()
            mime_type = magic.from_buffer(content, mime=True)
            return mime_type.startswith('application/')
    elif isinstance(file_path_or_content, bytes):
        mime_type = magic.from_buffer(file_path_or_content, mime=True)
        return mime_type.startswith('application/')
    else:
        raise TypeError("file_path_or_content must be either str or bytes.")
