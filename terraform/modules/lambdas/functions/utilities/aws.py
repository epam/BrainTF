from typing import Any, Dict, List, Tuple

import boto3
from boto3.dynamodb.conditions import Key

from config import config
from utilities.logger import logger


def _s3_client():
    """
    Creates and returns an Amazon S3 client instance using the defined boto3
    configuration.

    Returns:
        boto3.client: A boto3 client instance configured for S3.
    """
    return boto3.client('s3', config=config.boto3_config)


def _db_resource():
    """
    Creates and returns a Boto3 DynamoDB resource instance.

    This function utilizes the `boto3.resource` method with the specified
    configuration to create a DynamoDB resource object.

    Returns:
        boto3.resources.base.ServiceResource: A Boto3 resource instance
        for DynamoDB.
    """
    return boto3.resource('dynamodb', config=config.boto3_config)


def upload_files_to_s3(
        bucket_name: str,
        pull_number: int,
        file_paths_with_content: Dict[str, str],
) -> Dict[str, List[str]]:
    """
    Uploads a collection of files to an AWS S3 bucket, categorizing them into successfully
    uploaded and failed files. This function handles the upload process for multiple files
    and logs details about the success or failure of each upload.

    Args:
        bucket_name: The name of the S3 bucket where files will be uploaded.
        pull_number: The pull number used to construct the S3 key for each file.
        file_paths_with_content: A dictionary where keys are file paths (str) and values
            are the corresponding file contents (str) to be uploaded.

    Returns:
        A dictionary with two keys:
            "uploaded": A list of file paths that were successfully uploaded.
            "failed": A list of file paths that failed to upload.
    """
    uploaded: List[str] = []
    failed: List[str] = []

    for file_path, file_content in file_paths_with_content.items():

        s3_key = f"{config.path_to_artifacts}/{pull_number}/{file_path}"
        body = file_content.encode("utf-8")

        try:
            s3_client = _s3_client()
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=body,
                ExpectedBucketOwner=config.aws_account_id
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


def get_file_names_from_s3_directory(bucket_name: str, path_to_files: str) -> List[str]:
    """
    Retrieves the file names from a specified S3 directory.

    This function connects to an S3 bucket and retrieves the names of files within a
    specified directory. Directory placeholders and empty files are skipped. It handles
    pagination in case the number of objects exceeds the single API call limit.

    Args:
        bucket_name: Name of the S3 bucket to access.
        path_to_files: Path within the bucket to retrieve the files from.

    Returns:
        A list of file names found within the specified S3 directory, excluding directory
        placeholders and empty files.

    Raises:
        Any exceptions raised by the AWS SDK for Python (Boto3) while interacting
        with the S3 service.
    """
    file_names: List[str] = []
    continuation_token: str | None = None
    s3_client = _s3_client()
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


def get_all_files_from_s3_directory(
        bucket_name: str,
        path_to_files: str
) -> List[Tuple[str, str]]:
    """
    Retrieves all files from the specified S3 directory in a given bucket. A file is
    included only if it is not a directory or an empty object. The function retrieves
    both the file's key and its content.

    Args:
        bucket_name: The name of the S3 bucket to query.
        path_to_files: The directory path within the bucket to look for files.

    Returns:
        A list of tuples where each tuple contains the relative file key (str) and
        the content of the file (str).

    Raises:
        Exception: Propagates AWS SDK, response-shape, or UTF-8 decoding errors if they
            occur while listing or reading objects.
    """
    files: List[Tuple[str, str]] = []
    continuation_token: str | None = None
    s3_client = _s3_client()
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
            get_resp = s3_client.get_object(
                Bucket=bucket_name,
                Key=key,
                ExpectedBucketOwner=config.aws_account_id
            )
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
    Retrieves a list of files and their contents from a specified directory in an S3 bucket.

    This function connects to an S3 bucket and retrieves the contents of specific files based on
    provided file names and their directory path in the bucket. For each file that exists in the
    specified directory, it retrieves its body and appends a tuple containing the file name and
    its decoded content to the result list. Files not found in the directory are logged as warnings.
    Exceptions occurring during the retrieval process are logged as errors.

    Args:
        bucket_name (str): The name of the S3 bucket containing the files.
        path_to_files (str): The directory path in the S3 bucket where the files are located. Should
            include a trailing slash.
        file_names (List[str]): A list of file names to retrieve from the specified directory.

    Returns:
        List[Tuple[str, str]]: A list of tuples where each tuple contains a file name and its
        corresponding file content as a string.
    """
    files: List[Tuple[str, str]] = []
    s3_client = _s3_client()
    for file_name in file_names:
        # Construct the full S3 key
        key = f"{path_to_files}{file_name}"

        try:
            # Download file body
            get_resp = s3_client.get_object(
                Bucket=bucket_name,
                Key=key,
                ExpectedBucketOwner=config.aws_account_id
            )
            body_bytes = get_resp["Body"].read()
            body_text = body_bytes.decode("utf-8")

            files.append((file_name, body_text))
            logger.info(f"Successfully retrieved file '{file_name}' from S3.")

        except s3_client.exceptions.NoSuchKey:
            logger.warning(f"File '{file_name}' not found at key '{key}' in bucket '{bucket_name}'.")

        except Exception as e:
            logger.exception(f"Failed to retrieve file '{file_name}' from S3. Error: {e}")

    return files


def get_file_content_with_metadata_from_s3(s3_bucket: str, s3_key: str) -> Dict:
    """
    Retrieves the content and metadata of a specified file stored in an S3 bucket.

    This function connects to an S3 bucket to fetch the content of a file specified
    by its key, along with its metadata. The returned value contains the file
    content as a string and its associated metadata as a dictionary. In the event
    of any error during the process, the function raises an exception.

    Args:
        s3_bucket (str): The name of the S3 bucket where the file is stored.
        s3_key (str): The key identifying the file in the S3 bucket.

    Returns:
        Dict | None: A dictionary with the following keys:
            - "content": The file content as a string.
            - "metadata": A dictionary containing the file's metadata.
                Returns None if the operation fails.

    Raises:
        Exception: Propagates errors from S3 metadata or object retrieval after they
            are logged.
    """
    try:
        s3_client = _s3_client()
        # Get the metadata of the object
        head_object_response = s3_client.head_object(
            Bucket=s3_bucket,
            Key=s3_key,
            ExpectedBucketOwner=config.aws_account_id
        )

        # Retrieve the uploaded object from S3
        object_response: Dict[str, Any] = s3_client.get_object(
            Bucket=s3_bucket,
            Key=s3_key,
            ExpectedBucketOwner=config.aws_account_id
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
    """
    Retrieves messages from a database table based on the given partition key. The query results
    are ordered in ascending order by the sort key.

    The function utilizes a logger to document the process of fetching data, including when the
    query starts and the query response.

    Args:
        table_name: The name of the database table from which to retrieve the messages.
        partition_key: The partition key used to query the messages in the database.

    Returns:
        List of items retrieved from the database that match the given partition key.
    """
    logger.info(f"Getting messages from table '{table_name}' with partition key '{partition_key}'...")
    db = _db_resource()
    table = db.Table(table_name)

    # Query items using the partition key and sort by sort key
    response = table.query(
        KeyConditionExpression=Key('pk').eq(partition_key),
        ScanIndexForward=True  # True for ascending order, False for descending order
    )
    logger.debug(f"Response from DB -->\n{response}")
    return response['Items']


def put_messages_to_db(
        table_name: str,
        messages: List[Dict[str, Any]],
) -> None:
    """
    Insert multiple messages into a specified DynamoDB table using a transactional
    write operation. Ensures that each message is only inserted if its primary and
    sort keys do not already exist.

    Args:
        table_name: Name of the DynamoDB table to which the messages will be written.
        messages: List of dictionaries representing the items to be inserted. Each
            dictionary must provide attributes matching the schema of the table.

    """
    db = _db_resource()
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
    Deletes files from an Amazon S3 bucket under a specified prefix.

    This function connects to AWS S3 using a preconfigured client, retrieves the
    list of files under a given prefix in the specified bucket, and deletes those
    files in a single batch operation. It logs the status of the operation,
    including the number of files successfully deleted and any errors encountered
    during the process.

    Args:
        bucket_name (str): The name of the S3 bucket from which files will be deleted.
        path_to_files (str): The prefix/path under which files will be deleted
            in the specified S3 bucket.

    Raises:
        Exception: Any error that occurs during file deletion is logged, and the
            exception is re-raised to indicate a failure in the operation.
    """
    logger.info(f"Deleting files from bucket '{bucket_name}' with prefix '{path_to_files}'...")
    try:
        s3_client = _s3_client()
        # Fetch the list of objects with the specified prefix
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=path_to_files,
            ExpectedBucketOwner=config.aws_account_id
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
            },
            ExpectedBucketOwner=config.aws_account_id
        )

        deleted = delete_response.get("Deleted", [])
        errors = delete_response.get("Errors", [])

        logger.info(f"Deleted {len(deleted)} files successfully.")
        if errors:
            logger.error(f"Failed to delete {len(errors)} files. Errors: {errors}")

    except Exception as e:
        logger.exception(f"An error occurred while trying to delete files from S3. Error: {e}")
