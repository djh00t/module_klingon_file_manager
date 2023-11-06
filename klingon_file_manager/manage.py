# manage.py
"""
# Overview

This module provides a single way to manage file operations on both mounted
file systems and AWS S3 storage. It provides an interface for reading, writing,
and deleting files, with additional support for debugging and AWS
authentication.

# Functions

## manage_file
Main wrapper function that routes request to the appropriate submodules,
returning standardized responses and performing specific actions based on user
input.

# Usage Examples

To get a file from a local directory:
```python
>>> manage_file('get', '/path/to/local/file')
```
To get a file from an S3 bucket:
```python
>>> manage_file('get', 's3://bucket/file')
```
To post a file to a local directory:
```python
>>> manage_file('post', '/path/to/local/file', 'Hello, world!')
```
To post a file to an S3 bucket:
```python
>>> manage_file('post', 's3://bucket/file', 'Hello, world!')
```
To delete a file from a local directory:
```python
>>> manage_file('delete', '/path/to/local/file')
```
To delete a file from an S3 bucket:
```python
>>> manage_file('delete', 's3://bucket/file')
```
"""

from typing import Union, Dict, Optional, Callable
from .utils import is_binary_file, get_aws_credentials
from .delete import delete_file
from .post import post_file
from .get import get_file

# Use the get_aws_credentials function to get AWS credentials returned as a
# json object containing the following keys:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
aws_credentials = get_aws_credentials()
"""@private Get aws credentials from environment variables."""

def manage_file(
    action: str,
    path: str,
    content: str = None,
    md5: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    debug: bool = False,
) -> dict:
    """
    # Main function to manage file operations.

    ## Parameters
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | action    | string            | The action to perform. Can be 'get', 'post', or 'delete'. |   |
    | path      | string            | Path to the file |   |
    | content   | string or bytes   | The content to write to the file. Only used for 'post' action. |  |
    | md5       | string            | The MD5 hash of the content. Only used for 'post' action. | * See note |
    | metadata  | dictionary        | Additional metadata to include with the file | ^ See note |
    | debug     | boolean           | Flag to enable/disable debugging information in the response | False |

    **Note:**

    \\* If md5 is provided, it will be compared against the calculated MD5 hash
        of the content. If they do not match, the post will fail. If md5 hash
        is not provided, it will be calculated, returned in the response and
        will also be used to validate that the file arrived in tact by S3

    ^ Default metadata includes the following, if you add your own metadata, it
        will be merged with the default metadata:
    ```python
    {
        "md5": str,
        "filesize": int
    }
    ```

    ### Example Usage
    ```python
        with open(file_name, 'rb') as f:
            # Read the file content
            file_content = f.read()
        
        # Upload file
        result = file_upload(
            action='post',
            path="s3://test-bucket/tests/file_name",
            content=file_content,
            metadata=metadata,
            debug=False
        )
    ```
    
    ## Returns
    A dictionary containing the result of the operation. The schema of the returned dictionary is as follows:
    
    ```python
    {
        'action': str,
        'path': str,
        'content': str,
        'content_size': int,
        'binary': bool,
        'md5': str,
        'metadata': dict,
        'debug': dict,
    }
    ```
    
    ## Field Descriptions
    | Key       | Type              | Description |
    |-----------|-------------------|-------------|
    | action    | string            | The action to perform. Can be 'get', 'post', or 'delete' |
    | path      | string            | Path to the file |
    | content   | string or bytes   | A string representing the content or `<binary data>` placeholder if the content is binary/bytes, or `null` if the file could not be read. |
    | content_size | int             | An integer representing the size of the content in bytes, or `null` if the file could not be read. |
    | binary    | boolean           | A boolean indicating whether the file is binary (`true`) or text (`false`), or `null` if the file could not be read. |
    | md5       | string            | A string representing the MD5 hash of the content, or `null` if the file could not be read. |
    | metadata  | dictionary        | An object containing the metadata of the file, or `null` if the file could not be read. By default, the metadata will contain `md5` and `filesize` fields. |
    | debug     | dictionary        | An object containing debug information, or `null` if debugging is not enabled. |
    

    """

    # Initialize debug information
    debug_info = {}

    # Initialize result dictionary
    result = {
        'action': action,  # The action performed
        'path': path,  # The path to the file
        'content': "<binary data>" if isinstance(content, bytes) and action != 'get' else (content[:10] if isinstance(content, str) else content[:10].decode('utf-8')) if content and debug else content,  # The content of the file
        'content_size': len(content),  # The size of the content
        'binary': is_binary_file(content),  # Whether the content is binary
        'md5': md5,  # The MD5 hash of the content
        'metadata': metadata,  # The metadata of the file
        'debug': debug_info if debug else {},  # The debug information
    }

    try:
        if action == 'get':
            get_result = get_file(path, debug)
            result['status'] = get_result['status']
            result['content'] = get_result['content']
            result['binary'] = is_binary_file(result['content'])
            # Add the debug info for the get_file() function
            if debug or result['status'] == 500:
                debug_info['get_file'] = get_result['debug']
        elif action == 'post':
            result['binary'] = is_binary_file(content) if content else None
            debug_info['post_file_start'] = f"Starting post_file with path={path}, content={content[:10]}, md5={md5}, metadata={metadata}"
            post_result = post_file(path, content, md5, metadata, debug)
            result['status'] = post_result['status']
            # Add the debug info for the post_file() function
            if debug or result['status'] == 500:
                debug_info['post_file'] = post_result['debug']
            return result
        elif action == 'delete':
            delete_result = delete_file(path, debug)
            result['status'] = delete_result['status']
            # Add the debug info for the delete_file() function
            if debug or result['status'] == 500:
                debug_info['delete_file'] = delete_result['debug']
        else:
            result['status'] = 500
            debug_info['error'] = 'Invalid action'
    except Exception as exception:
        result['status'] = 500
        result['error_message'] = str(exception)
        # Add the debug info for the exception
        debug_info['exception'] = str(exception) if debug else None
        debug_info['error_message'] = str(exception) if debug else None
    # If the debug flag is not set and there was no failure, remove the debug field
    # No need to delete the 'debug' key as it will be empty if debug is False
    if not debug and result['status'] != 500:
        del result['debug']
