# get.py
"""
Module for getting files from local and AWS S3 storage.

This module provides a centralized way to manage file operations on both
local and AWS S3 storage. It leverages utility functions from the `utils` module
and specific actions from `get`, `post`, and `delete` modules.

Functions:
    get_file: Function for getting files.

Example:
    To get a file from a local directory:
    >>> manage_file('get', '/path/to/local/file')
    
    To get a file from an S3 bucket:
    >>> manage_file('get', 's3://bucket/file')
    ...
"""


import os
import boto3
from typing import Union, Dict
from .utils import get_aws_credentials, is_binary_file


def get_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """
    Gets a file from a given path.

    This function gets a file from a specified path. The path can either be a
    local directory or an S3 bucket.

    Args:
        path: The path of the file to get.
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        A dictionary containing the status of the get operation. The schema
        is as follows:
            {
                "status": int,          # HTTP-like status code
                "message": str,         # Message describing the outcome
                "content": Union[str, bytes],  # The actual file content
                "binary": bool,         # Flag indicating if the content is binary
                "debug": Dict[str, str] # Debug information
            }
    """
    debug_info = {}

    try:
        if path.startswith("s3://"):
            debug_info.update(_get_from_s3(path, debug))
        else:
            debug_info.update(_get_from_local(path, debug))

        return debug_info

    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": f"Failed to get file: {str(exception)}" if debug else "Failed to get file.",
            "content": None,
            "binary": None,
            "debug": debug_info if debug else {},
        }


def _get_from_s3(path: str, debug: bool) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """
    Gets a file from an S3 bucket.

    Args:
        path: The S3 path where the file should be read from.
        debug: Flag to enable debugging.

    Returns:
        A dictionary containing the status of the get operation from S3.
    """
    s3_uri_parts = path[5:].split("/", 1)
    bucket_name = s3_uri_parts[0]
    key = s3_uri_parts[1]

    debug_info = {
        "s3_uri_parts": s3_uri_parts,
        "bucket_name": bucket_name,
        "key": key,
    }
    s3 = resource('s3')
    s3_object = s3.Object(bucket_name, key)

    try:
        content = s3_object.get()['Body'].read()
    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": "Failed to get file from S3.",
            "content": None,
            "binary": None,
            "debug": debug_info if debug else {},
        }

    return {
        "status": 200,
        "message": "File read successfully from S3.",
        "content": content,
        "binary": True,
        "debug": debug_info if debug else {},
    }



def _get_from_local(path: str, debug: bool) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """
    Gets a file from a local directory.

    Args:
        path: The local path where the file should be read from.
        debug: Flag to enable debugging.

    Returns:
        A dictionary containing the status of the get operation from the local directory.
    """
    debug_info = {}

    try:
        with open(path, "rb") as file:
            content = file.read()
    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": "Failed to get file from local.",
            "content": None,
            "binary": None,
            "debug": debug_info if debug else {},
        }
        
    is_binary = is_binary_file(content)

    return {
        "status": 200,
        "message": "File read successfully.",
        "content": content,
        "binary": is_binary,
        "debug": debug_info if debug else {},
    }
