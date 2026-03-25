from typing import Any, Dict, List, Tuple

import boto3
from boto3.dynamodb.conditions import Key
from config import config
from utilities.logger import logger

ssm = boto3.client('ssm', config=config.boto3_config)

s3 = boto3.resource('s3', config=config.boto3_config)

# Create an S3 client
s3_client = boto3.client('s3', config=config.boto3_config)

db = boto3.resource('dynamodb', config=config.boto3_config)

# Initialize STS client
sts_client = boto3.client('sts', config=config.boto3_config)


# Extract the account ID
# aws_account_id: str = sts_client.get_caller_identity()['Account']


def get_parameter_from_ssm(parameter_name: str) -> str:
    """Retrieve a parameter value from AWS Systems Manager Parameter Store.

    Args:
        parameter_name (str): The name of the parameter to retrieve.

    Returns:
        str: The decrypted value of the parameter.
    """
    response: Dict[str, Any] = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']


def upload_files_to_s3(
        bucket_name: str,
        pull_number: int,
        file_paths_with_content: Dict[str, str],
) -> Dict[str, List[str]]:
    """
    Uploads multiple files to an Amazon S3 bucket under a pull-request-based prefix.

    Args:
        bucket_name (str): Target S3 bucket name.
        pull_number (int): Pull request number used for key construction.
        file_paths_with_content (Dict[str, str]):
            Mapping of file path -> file content.

    Returns:
        Dict[str, List[str]]: Uploaded and failed file paths.
    """
    uploaded: List[str] = []
    failed: List[str] = []

    for file_path, file_content in file_paths_with_content.items():
        # TODO: Get path to artifacts from config
        s3_key = f"artifacts/{pull_number}/{file_path}"
        body = file_content.encode("utf-8")

        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=body,
                # ExpectedBucketOwner=aws_account_id
            )
            uploaded.append(file_path)
            logger.info(
                f"File '{file_path}' uploaded successfully to bucket "
                f"'{bucket_name}' with key '{s3_key}'."
            )

        except Exception as e:
            failed.append(file_path)
            logger.exception(
                f"Failed to upload file '{file_path}' to bucket '{bucket_name}'. Error: {e}"
            )

    return {
        "uploaded": uploaded,
        "failed": failed,
    }


def upload_file_s3(bucket_name: str, pull_number: int, full_path_to_file: str, file_content: str):
    """
    Uploads a file to an Amazon S3 bucket under a specified key path.

    This function encodes the given file content into UTF-8 and constructs
    an S3 key path for the file using the provided pull request number and
    file path. It attempts to upload the file to the specified bucket and logs
    a success or failure message.

    Args:
        full_path_to_file (str): The file path/name to upload in the S3 bucket.
        bucket_name (str): The name of the target S3 bucket.
        pull_number (int): The pull request number used for key construction.
        file_content (str): The content of the file to upload, as a string.
    """

    s3_key = f"artifacts/{pull_number}/{full_path_to_file}"

    body = file_content.encode('utf-8')

    try:
        # Upload the file
        s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=body,
                             # ExpectedBucketOwner=aws_account_id
                             )
        logger.info(f"File '{full_path_to_file}' uploaded successfully to bucket '{bucket_name}' with key '{s3_key}'.")

    except Exception as e:
        logger.info(f"Failed to upload file '{full_path_to_file}' to bucket '{bucket_name}'. Error: {e}")


def get_files_from_s3_directory_(bucket_name: str, path_to_files: str) -> List[tuple[str, str]]:
    # path_to_mr_artifacts = f"{config.path_to_artifacts}/{merge_request_id}/"
    bucket = s3.Bucket(bucket_name)
    files_key_content = [
        (obj.key.removeprefix(path_to_files), obj.get()['Body'].read().decode('utf-8'))
        for obj in bucket.objects.filter(Prefix=path_to_files)
        if not obj.key.endswith('/') and obj.size > 0  # Filter out directories and empty objects
    ]

    return files_key_content


def get_file_names_from_s3_directory(bucket_name: str, path_to_files: str) -> List[str]:
    """
    Retrieve only file names (object keys without the prefix) from an S3 'directory'
    in a cost‑efficient way (no object bodies are downloaded).

    Args:
        bucket_name (str): Name of the S3 bucket.
        path_to_files (str): Prefix/path to the files (e.g. 'artifacts/123/').

    Returns:
        List[str]: List of file names under the given prefix.
    """
    file_names: List[str] = []
    continuation_token = None

    while True:
        list_kwargs: Dict[str, Any] = {
            "Bucket": bucket_name,
            "Prefix": path_to_files,
        }
        if continuation_token:
            list_kwargs["ContinuationToken"] = continuation_token

        response = s3_client.list_objects_v2(**list_kwargs)

        contents = response.get("Contents", [])
        for obj in contents:
            key = obj["Key"]
            # Skip "directory" placeholders
            if key.endswith("/") or obj.get("Size", 0) == 0:
                continue
            file_names.append(key.removeprefix(path_to_files))

        if response.get("IsTruncated"):
            continuation_token = response.get("NextContinuationToken")
        else:
            break

    return file_names


def get_all_files_from_s3_directory(bucket_name: str, path_to_files: str) -> List[Tuple[str, str]]:
    """
    Retrieve (filename, file_content) tuples from an S3 prefix using s3_client.
    Downloads only object bodies for actual files (skips directories and zero-size objects).
    """
    files: List[Tuple[str, str]] = []
    continuation_token = None

    while True:
        list_kwargs = {
            "Bucket": bucket_name,
            "Prefix": path_to_files,
        }
        if continuation_token:
            list_kwargs["ContinuationToken"] = continuation_token

        response = s3_client.list_objects_v2(**list_kwargs)
        contents = response.get("Contents", [])

        for obj in contents:
            key = obj["Key"]
            size = obj.get("Size", 0)

            # Skip directories/empty objects
            if key.endswith("/") or size == 0:
                continue

            # Download file body
            get_resp = s3_client.get_object(Bucket=bucket_name, Key=key)
            body_bytes = get_resp["Body"].read()
            body_text = body_bytes.decode("utf-8")

            files.append((key.removeprefix(path_to_files), body_text))

        if response.get("IsTruncated"):
            continuation_token = response.get("NextContinuationToken")
        else:
            break

    return files


def get_particular_files_from_s3_directory(
        bucket_name: str,
        path_to_files: str,
        file_names: List[str]
) -> List[Tuple[str, str]]:
    """
    Retrieve (filename, file_content) tuples for specific files from an S3 prefix.
    Downloads only the requested files by their names (relative to path_to_files).
    
    Args:
        bucket_name (str): Name of the S3 bucket.
        path_to_files (str): Prefix/path to the files (e.g. 'artifacts/123/').
        file_names (List[str]): List of file names to retrieve (relative to path_to_files).
    
    Returns:
        List[Tuple[str, str]]: List of (filename, file_content) tuples for requested files.
    """
    files: List[Tuple[str, str]] = []

    for file_name in file_names:
        # Construct the full S3 key
        key = f"{path_to_files}{file_name}"

        try:
            # Download file body
            get_resp = s3_client.get_object(Bucket=bucket_name, Key=key)
            body_bytes = get_resp["Body"].read()
            body_text = body_bytes.decode("utf-8")

            files.append((file_name, body_text))
            logger.info(f"Successfully retrieved file '{file_name}' from S3.")

        except s3_client.exceptions.NoSuchKey:
            logger.warning(f"File '{file_name}' not found at key '{key}' in bucket '{bucket_name}'.")
        except Exception as e:
            logger.exception(f"Failed to retrieve file '{file_name}' from S3. Error: {e}")

    return files


def get_file_content_with_metadata_from_s3(s3_bucket: str, s3_key: str) -> Dict | None:
    try:
        # Get the metadata of the object
        head_object_response = s3_client.head_object(
            Bucket=s3_bucket,
            Key=s3_key,
            # ExpectedBucketOwner=aws_account_id
        )

        # Retrieve the uploaded object from S3
        object_response: Dict[str, Any] = s3_client.get_object(
            Bucket=s3_bucket,
            Key=s3_key,
            # ExpectedBucketOwner=aws_account_id
        )

        # Extract metadata
        object_metadata: Dict = head_object_response.get('Metadata', {})

        # Read and decode the file content
        content: str = object_response['Body'].read().decode('utf-8')
        logger.info(f"File content: {content}")
        logger.info(f"File metadata: {object_metadata}")
        return {"content": content, "metadata": object_metadata}

    except Exception as e:
        raise Exception(f"Error occurred while reading the object from S3: {e}")


def get_messages_from_db(table_name: str, partition_key: str) -> list:
    logger.info(f"Getting messages from table '{table_name}' with partition key '{partition_key}'...")
    table = db.Table(table_name)

    # Query items using the partition key and sort by sort key
    response = table.query(
        KeyConditionExpression=Key('pk').eq(partition_key),
        ScanIndexForward=True  # True for ascending order, False for descending order
    )
    logger.debug(f"Response from DB -->\n{response}")
    return response['Items']


def put_message_to_db(table_name: str, commit_short_sha: str, sort_key, message: str):
    table = db.Table(table_name)
    user_item = {
        'pk': commit_short_sha,  # Partition key
        'sk': sort_key,  # Sort key
        'content': message,
        'role': 'user'
    }

    # Put the item into the table
    table.put_item(Item=user_item)


def put_messages_to_db(
        table_name: str,
        messages: List[Dict[str, Any]],
) -> None:
    client = db.meta.client

    transact_items = [
        {
            "Put": {
                "TableName": table_name,
                "Item": message,
                "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
            }
        }
        for message in messages
    ]

    client.transact_write_items(TransactItems=transact_items)


def delete_files_from_s3(bucket_name: str, path_to_files: str) -> None:
    """
    Deletes all files from an S3 'directory' (specified by the prefix) in the bucket.

    Args:
        bucket_name (str): Name of the S3 bucket.
        path_to_files (str): Prefix/directory path in the bucket to delete files from.
    """
    logger.info(f"Deleting files from bucket '{bucket_name}' with prefix '{path_to_files}'...")
    try:
        # Fetch the list of objects with the specified prefix
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=path_to_files
        )
        objects = response.get("Contents", [])

        # Extract object keys for deletion
        object_keys = [{"Key": obj["Key"]} for obj in objects]

        if not object_keys:
            logger.info(f"No files found under prefix '{path_to_files}' to delete.")
            return

        # Delete all objects in a single batch
        delete_response = s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={
                "Objects": object_keys,
            }
        )

        deleted = delete_response.get("Deleted", [])
        errors = delete_response.get("Errors", [])

        logger.info(f"Deleted {len(deleted)} files successfully.")
        if errors:
            logger.error(f"Failed to delete {len(errors)} files. Errors: {errors}")

    except Exception as e:
        logger.exception(f"An error occurred while trying to delete files from S3. Error: {e}")
