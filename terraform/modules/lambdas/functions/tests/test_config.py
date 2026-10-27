import pytest


class MockBoto3Config:
    def __init__(self, connect_timeout, read_timeout):
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout


@pytest.fixture
def config_class(patched_environment):
    from config import _ConfigLambda

    return _ConfigLambda


def test_config_loads_defaults(config_class, patched_environment, monkeypatch):
    for variable in ("VCS_PROVIDER", "ARTIFACTS_PATH", "LOG_LEVEL",
                     "RAG_ENABLED", "TTL_DELTA_DAYS"):
        patched_environment.delenv(variable, raising=False)

    monkeypatch.setattr("config.Config", MockBoto3Config)
    config = config_class()

    assert config.vcs_provider == "github"
    assert config.path_to_artifacts == "artifacts"
    assert config.log_level == "INFO"
    assert config.rag_enabled is False
    assert config.ttl_delta_days == 30
    assert config.default_timeout == (361, 361)
    assert config.boto3_config.connect_timeout == 361
    assert config.boto3_config.read_timeout == 361


@pytest.mark.parametrize("provider", ["github", "gitlab", "bitbucket"])
def test_config_accepts_supported_vcs_providers(config_class, patched_environment, provider):
    patched_environment.setenv("VCS_PROVIDER", provider)

    assert config_class().vcs_provider == provider


@pytest.mark.parametrize(
    ("variable", "value", "message"),
    [
        ("VCS_PROVIDER", "bitbucket-server", "Invalid VCS_PROVIDER"),
        ("VCS_TOKEN_NAME", "", "VCS_TOKEN_NAME environment variable is required"),
        ("VCS_API_ENDPOINT", "", "VCS_API_ENDPOINT environment variable is required"),
        ("VCS_API_ENDPOINT", "http://gitlab.example", "must start with https://"),
        ("VCS_API_ENDPOINT", "https://gitlab.example/api/v4", "must not end with /api/v4"),
        ("WEBHOOK_SECRET_NAME", "", "WEBHOOK_SECRET_NAME environment variable is required"),
        ("ARTIFACTS_BUCKET", "", "ARTIFACTS_BUCKET environment variable is required"),
        ("ARTIFACTS_PATH", "", "ARTIFACTS_PATH cannot be empty"),
        ("AI_API_TOKEN_NAME", "", "AI_API_TOKEN_NAME environment variable is required"),
        ("LLM_MODEL", "", "LLM_MODEL environment variable is required"),
        ("AI_TEMPERATURE", "", "AI_TEMPERATURE environment variable is required"),
        ("AI_API_BASE_URL", "", "AI_API_BASE_URL environment variable is required"),
        ("AI_API_BASE_URL", "http://ai.example", "must start with https://"),
        ("DYNAMODB_TABLE_NAME", "", "DYNAMODB_TABLE_NAME environment variable is required"),
        ("LOG_LEVEL", "TRACE", "Invalid LOG_LEVEL"),
    ],
)
def test_config_rejects_invalid_values(config_class, patched_environment, variable, value, message):
    patched_environment.setenv(variable, value)

    with pytest.raises(ValueError, match=message):
        config_class()


@pytest.mark.parametrize(
    "variable",
    [
        "VCS_TOKEN_NAME",
        "VCS_API_ENDPOINT",
        "WEBHOOK_SECRET_NAME",
        "AI_API_TOKEN_NAME",
        "LLM_MODEL",
        "AI_API_BASE_URL",
        "DYNAMODB_TABLE_NAME",
    ],
)
def test_config_rejects_missing_required_values(config_class, patched_environment, variable):
    patched_environment.delenv(variable, raising=False)

    with pytest.raises(ValueError):
        config_class()


@pytest.mark.parametrize("temperature", ["0", "0.0", "2"])
def test_config_accepts_temperature_boundaries(config_class, patched_environment, temperature):
    patched_environment.setenv("AI_TEMPERATURE", temperature)

    assert config_class().ai_temperature == float(temperature)


@pytest.mark.parametrize(
    ("temperature", "message"),
    [
        ("not-a-number", "AI_TEMPERATURE must be a valid number"),
        ("-0.1", "AI_TEMPERATURE must be between zero and two"),
        ("2.1", "AI_TEMPERATURE must be between zero and two"),
    ],
)
def test_config_rejects_invalid_temperature(config_class, patched_environment, temperature, message):
    patched_environment.setenv("AI_TEMPERATURE", temperature)

    with pytest.raises(ValueError, match=message):
        config_class()


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes", "YeS"])
def test_config_enables_rag_for_truthy_values(config_class, patched_environment, value):
    patched_environment.setenv("RAG_ENABLED", value)

    assert config_class().rag_enabled is True


@pytest.mark.parametrize("value", ["false", "0", "no", ""])
def test_config_disables_rag_for_falsey_values(config_class, patched_environment, value):
    patched_environment.setenv("RAG_ENABLED", value)

    assert config_class().rag_enabled is False


@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_config_accepts_supported_log_levels(config_class, patched_environment, log_level):
    patched_environment.setenv("LOG_LEVEL", log_level.lower())

    assert config_class().log_level == log_level


def test_config_rejects_non_integer_ttl(config_class, patched_environment):
    patched_environment.setenv("TTL_DELTA_DAYS", "thirty")

    with pytest.raises(ValueError):
        config_class()


def test_config_retrieves_secrets_from_ssm(config_class, ssm_setup, expected_token_gitlab):
    config = config_class()

    assert config.vcs_api_token == expected_token_gitlab
    assert config.webhook_secret == expected_token_gitlab
    assert config.ai_api_token == "token"


def test_config_caches_aws_account_id(config_class, ssm_setup):
    config = config_class()

    assert config.aws_account_id == "123456789012"
    assert config.aws_account_id == "123456789012"
    assert "aws_account_id" in vars(config)
