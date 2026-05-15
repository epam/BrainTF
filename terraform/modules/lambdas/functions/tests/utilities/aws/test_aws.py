import boto3
from tests.data.file_samples import MAIN_TF_FILE

TEST_BUCKET = "test-bucket"
TEST_PREFIX = ""
AWS_REGION = "eu-central-1"
VALIDATE_TF_CONTENT = 'variable "aws_region" { default = "eu-central-1" }\n'


def _s3_list_response(contents, is_truncated=False, token=None):
    response = {
        "IsTruncated": is_truncated,
        "Contents": contents,
        "KeyCount": len(contents),
        "Name": TEST_BUCKET,
        "Prefix": TEST_PREFIX,
        "MaxKeys": 1000,
    }
    if token:
        response["NextContinuationToken"] = token
    return response


class StubbedS3Client:
    def __init__(self, responses, call_counter, wrapped=None):
        self._responses = responses
        self._call_counter = call_counter
        self._wrapped = wrapped

    def list_objects_v2(self, **kwargs):
        index = self._call_counter["count"]
        self._call_counter["count"] += 1
        return self._responses[index]

    def __getattr__(self, name):
        if self._wrapped is None:
            raise AttributeError(name)
        return getattr(self._wrapped, name)


def test_get_parameter_from_ssm(patched_environment, monkeypatch, ssm_setup):
    from utilities.aws import get_parameter_from_ssm

    parameter_value = get_parameter_from_ssm("test-parameter")
    assert parameter_value == "test-value"


def test_get_file_names_from_s3_directory_success(s3_setup):
    from utilities.aws import get_file_names_from_s3_directory

    result = get_file_names_from_s3_directory(TEST_BUCKET, TEST_PREFIX)
    assert isinstance(result, list)
    assert len(result) == 2
    assert "main.tf" in result
    assert "validate.tf" in result


def test_get_all_files_from_s3_directory_success(s3_setup):
    from utilities.aws import get_all_files_from_s3_directory

    result = get_all_files_from_s3_directory(TEST_BUCKET, TEST_PREFIX)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result == [("main.tf", MAIN_TF_FILE), ("validate.tf", VALIDATE_TF_CONTENT)]


def test_get_particular_files_from_s3_directory_success(s3_setup):
    from utilities.aws import get_particular_files_from_s3_directory

    result = get_particular_files_from_s3_directory(TEST_BUCKET, TEST_PREFIX, ["main.tf"])
    assert isinstance(result, list)
    assert len(result) == 1
    assert result == [("main.tf", MAIN_TF_FILE)]


def test_get_file_names_from_s3_directory_pagination_truncated_then_not_truncated(s3_setup, monkeypatch):
    from utilities.aws import get_file_names_from_s3_directory

    responses = [
        _s3_list_response([{"Key": "main.tf", "Size": 10}], is_truncated=True, token="token-1"),
        _s3_list_response([{"Key": "validate.tf", "Size": 20}], is_truncated=False),
    ]
    call_counter = {"count": 0}
    stubbed_client = StubbedS3Client(responses, call_counter)
    monkeypatch.setattr("utilities.aws._s3_client", lambda: stubbed_client)

    result = get_file_names_from_s3_directory(TEST_BUCKET, TEST_PREFIX)

    assert result == ["main.tf", "validate.tf"]
    assert call_counter["count"] == 2


def test_get_all_files_from_s3_directory_pagination_truncated_then_not_truncated(s3_setup, monkeypatch):
    from utilities.aws import get_all_files_from_s3_directory

    real_s3 = boto3.client("s3")
    responses = [
        _s3_list_response([{"Key": "main.tf", "Size": 10}], is_truncated=True, token="token-1"),
        _s3_list_response([{"Key": "validate.tf", "Size": 20}], is_truncated=False),
    ]
    call_counter = {"count": 0}
    stubbed_client = StubbedS3Client(responses, call_counter, wrapped=real_s3)
    monkeypatch.setattr("utilities.aws._s3_client", lambda: stubbed_client)

    result = get_all_files_from_s3_directory(TEST_BUCKET, TEST_PREFIX)

    assert result == [("main.tf", MAIN_TF_FILE), ("validate.tf", VALIDATE_TF_CONTENT)]
    assert call_counter["count"] == 2


def test_get_file_names_from_s3_directory_zero_size_object(s3_setup, monkeypatch):
    from utilities.aws import get_file_names_from_s3_directory

    real_s3 = boto3.client("s3")
    responses = [_s3_list_response([{"Key": "empty.tf", "Size": 0}], is_truncated=False)]
    call_counter = {"count": 0}
    stubbed_client = StubbedS3Client(responses, call_counter, wrapped=real_s3)
    monkeypatch.setattr("utilities.aws._s3_client", lambda: stubbed_client)

    result = get_file_names_from_s3_directory(TEST_BUCKET, TEST_PREFIX)

    assert result == []
    assert call_counter["count"] == 1


def test_get_file_names_from_s3_directory_none_file_object(s3_setup, monkeypatch):
    from utilities.aws import get_file_names_from_s3_directory

    responses = [_s3_list_response([{"Key": "empty/", "Size": 10}], is_truncated=False)]
    call_counter = {"count": 0}
    stubbed_client = StubbedS3Client(responses, call_counter)
    monkeypatch.setattr("utilities.aws._s3_client", lambda: stubbed_client)

    result = get_file_names_from_s3_directory(TEST_BUCKET, TEST_PREFIX)

    assert result == []
    assert call_counter["count"] == 1


def test_get_all_files_from_s3_directory_none_file_object(s3_setup, monkeypatch):
    from utilities.aws import get_all_files_from_s3_directory

    responses = [_s3_list_response([{"Key": "empty/", "Size": 10}], is_truncated=False)]
    call_counter = {"count": 0}
    stubbed_client = StubbedS3Client(responses, call_counter)
    monkeypatch.setattr("utilities.aws._s3_client", lambda: stubbed_client)

    result = get_all_files_from_s3_directory(TEST_BUCKET, TEST_PREFIX)

    assert result == []
    assert call_counter["count"] == 1


def test_get_all_files_from_s3_directory_zero_size_object(s3_setup, monkeypatch):
    from utilities.aws import get_all_files_from_s3_directory

    responses = [_s3_list_response([{"Key": "empty.tf", "Size": 0}], is_truncated=False)]
    call_counter = {"count": 0}
    stubbed_client = StubbedS3Client(responses, call_counter)
    monkeypatch.setattr("utilities.aws._s3_client", lambda: stubbed_client)

    result = get_all_files_from_s3_directory(TEST_BUCKET, TEST_PREFIX)

    assert result == []
    assert call_counter["count"] == 1
