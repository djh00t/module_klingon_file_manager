# manage.py
"""
# Overview

This module provides a single way to manage file operations on both mounted
file systems and AWS S3 storage. It provides an interface for reading, writing,
and deleting files, with additional support for debugging and AWS
authentication.

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
To move a file from a local directory to another local directory:
```python
>>> move_file('/path/to/local/file', '/path/to/local/destination')
```
To move a file from a local directory to an S3 bucket:
```python
>>> move_file('/path/to/local/file', 's3://bucket/file')
```
"""

from typing import Union, Dict, Optional, Callable
import requests
import os
from .utils import is_binary_file, get_aws_credentials, get_md5_hash, get_md5_hash_filename,check_file_exists
from .delete import delete_file
from .post import post_file
from .get import get_file

# Use the get_aws_credentials function to get AWS credentials returned as a
# json object containing the following keys:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
aws_credentials = get_aws_credentials()
"""@private Get aws credentials from environment variables."""

class FilesystemRouter:
    """
    # Filesystem Router

    `FilesystemRouter` is a class that looks at requests it receives and routes
    the request to the correct submodule for handling.

    ## Arguments
    
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | list      | list            | A list containing the files to route | list |

    ## Returns

    The returns vary based on the function called, however the following is the
    minimum content that should be returned in the dictionary:

    ```python
    {
        'status': int,
        'message': str,
        'debug': dict,
    }
    ```
    """


    def remove_files(self, files):
        """
        # Remove Files
        Removes all files in the given list, if they exist by passing them to
        the `delete_file` function.

        ## Args
        files: A list of file paths.

        ## Returns
        
        """
        for file in files:
            if exists := check_file_exists(file):
                result = delete_file(file)

                # Capture result variables
                status = result['status']
                message = result['message']
                debug = result['debug']

                return {
                    "status": status,
                    "message": message,
                    "debug": debug
                }
                
            else:
                return {
                    "status": 404,
                    "message": f"File {file} not found.",
                    "debug": {}
                }

def manage_file(
    action: str,
    path: str,
    content: str = None,
    md5: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    debug: bool = False,
) -> dict:
    """
    # Manage File
    Main function to manage file operations.

    ## Arguments
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
        'content_size': len(content) if content else None,  # The size of the content
        'binary': is_binary_file(content) if content else None,  # Whether the content is binary
        'md5': md5,  # The MD5 hash of the content
        'metadata': metadata,  # The metadata of the file
        'debug': debug_info if debug else {},  # The debug information
    }

    print(f"DEBUG: result={result}")

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
            post_result = post_file(
                path=path, 
                content=content, 
                md5=md5,
                metadata=metadata, 
                debug=debug
                )
            result['status'] = post_result['status']
            # Add the debug info for the post_file() function
            if debug or result['status'] == 500:
                debug_info['post_file'] = post_result['debug']
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
    finally:
        # If the debug flag is not set and there was no failure, remove the debug field
        # No need to delete the 'debug' key as it will be empty if debug is False
        if not debug and result['status'] != 500:
            del result['debug']
        return result

def move_file(source_path, dest_path, debug=False):
    """
    # Move File
    Moves a file from a source path to a destination path.

    This function uses auxiliary functions from `get.py`, `post.py`, and `delete.py` to first retrieve
    the file from the source path, then save it to the destination path, and finally delete the original file.
    It also checks if the file is binary and handles it accordingly during the operations. MD5 checksums are used
    to verify the integrity of the file after moving.

    ## Arguments

    | Name         | Type    | Description                                                  | Default |
    |--------------|---------|--------------------------------------------------------------|---------|
    | source_path  | str     | The path (local or S3 URL) of the file to move.              | None    |
    | dest_path    | str     | The destination path (local or S3 URL) to move the file to.  | None    |
    | debug        | bool    | Flag to enable detailed error messages and logging.          | False   |

    ## Returns
    A dictionary with the following keys:
    
    | Key          | Type    | Description                                                  |
    |--------------|---------|--------------------------------------------------------------|
    | status       | int     | The HTTP status code indicating the outcome of the operation. |
    | message      | str     | A message describing the outcome of the operation.            |
    | source       | str     | The source path provided as input.                            |
    | destination  | str     | The destination path provided as input.                       |
    | md5          | str     | The MD5 checksum of the moved file.                           |

    If the operation is successful, the status will be 200, and the message will indicate success.
    If the operation fails, the status will be 500, and the message will provide an error explanation.

    Example of a successful return:
    {
        "status": 200,
        "message": "File moved successfully.",
        "source": "path/to/source/file.txt",
        "destination": "path/to/destination/file.txt",
        "md5": "1B2M2Y8AsgTpgAmY7PhCfg=="
    }

    Example of a failed return:
    {
        "status": 500,
        "message": "An error occurred while moving the file: [error description]",
        "debug": {
            "source_path": source_path, 
            "dest_path": dest_path, 
            "get_md5": get_md5, 
            "post_md5": post_md5, 
            "dest_md5": dest_md5, 
            "debug": {
                "get": get_result,
                "post": post_result,
                }
            }
        }
    }
    """

    try:
        # Check if the file is binary
        binary = is_binary_file(source_path)

        # Retrieve the file using get.py functionality
        get_result = get_file(source_path, debug)

        # GET return vars
        get_status = get_result['status']
        get_message = get_result['message']
        get_content = get_result['content']
        get_binary = get_result['binary']
        get_debug = get_result['debug']
        get_md5 = get_md5_hash_filename(source_path)

        # Debugging
        # If debug is True print debug info
        if debug:
            print("===========================================================================")
            print(f"DEBUG:                       GET STATUS: {get_status}")
            print(f"DEBUG:                      GET MESSAGE: {get_message}")
            print(f"DEBUG:                          GET MD5: {get_md5}")
            print()
            
        # If get_status isn't 200, return a 500 error
        if get_result['status'] != 200:
            return {
                "status": 500, 
                "message": "Failed to retrieve the file.",
                "debug": {
                    "get": get_result
                }
            }

        # Save the file to the destination using post.py functionality
        post_result = post_file(
            path=dest_path, 
            content=get_content,
            debug=debug  # Ensure debug flag is passed correctly
            )

        # Collect POST return vars
        post_status = post_result['status']
        post_message = post_result['message']
        post_md5 = post_result['md5']
        post_debug = post_result['debug']

        # If debug is True print debug info
        if debug:
            print(f"DEBUG:                      POST STATUS: {post_status}")
            print(f"DEBUG:                     POST MESSAGE: {post_message}")
            print(f"DEBUG:                         POST MD5: {post_md5}")
            print()
        
        if post_result['status'] != 200:
            return {
                "status": 500, 
                "message": "Failed to save the file to the destination.",
                "debug": {
                    "get": get_result,
                    "post": post_result
                }
            }

        # Delete the file from the source path using delete.py functionality
        delete_result = delete_file(source_path, debug)

        # Collect DELETE return vars
        delete_status = delete_result['status']
        delete_message = delete_result['message']
        delete_debug = delete_result['debug']

        # Retrieve the file from the destination path to verify MD5 checksum
        dest_md5 = get_md5_hash_filename(dest_path)
            
        # If debug is True print debug info
        if debug:
            print(f"DEBUG:                    DELETE STATUS: {delete_status}")
            print(f"DEBUG:                   DELETE MESSAGE: {delete_message}")
            print(f"DEBUG:                  DESTINATION MD5: {dest_md5}")
            print()
            if get_md5 == post_md5 == dest_md5:
                print(f"DEBUG:                   ALL MD5 CHECKSUMS MATCH!!!")
            else:
                Exception("MD5 checksums do not match.")
            print("===========================================================================")

            
        if delete_result['status'] != 200:
            return {
                "status": 500, "message": "Failed to delete the file from the source.",
                "debug": {
                    "get": get_result,
                    "post": post_result,
                    "delete": delete_result
                }
            }

        if get_md5 == post_md5 == dest_md5:
            # Return the success result
            return {
                "status": 200,
                "message": "File moved successfully.",
                "source": source_path,
                "destination": dest_path,
                "md5": dest_md5,
                "debug": {
                    "get": get_result,
                    "post": post_result,
                    "delete": delete_result
                    } if debug else ""
            }

    except Exception as e:
        # If there's any exception, return an error message
        return {
            "status": 500,
            "message": "An error occurred while moving the file: " + str(e)
        }
