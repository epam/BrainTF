from tests.data.file_samples import DEMO_BROKEN_MAIN_TF_FILE


def test_make_prompt_block_with_errors_and_files_tflint(
        patched_environment, log_file_text_tflint, webhook_event_command_bot_list_github):
    from config import config
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files
    event = webhook_event_command_bot_list_github
    event["metadata"]["tool_name"] = "tflint"
    patched_environment.setattr(config, "rag_enabled", True)
    patched_environment.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda current_event, paths_to_files: [("demo/broken/main.tf", DEMO_BROKEN_MAIN_TF_FILE)]
    )
    prompt = make_prompt_block_with_errors_and_files(event, log_file_text_tflint)

    assert "terraform_required_version" in prompt


def test_make_prompt_block_with_tflint_guides_when_rag_enabled(
        patched_environment, monkeypatch, log_file_text_tflint, webhook_event_command_bot_list_github):
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files

    event = webhook_event_command_bot_list_github
    event["metadata"]["tool_name"] = "tflint"
    retrieved_errors = []

    def retrieve_guides(errors):
        retrieved_errors.append(errors)
        return "terraform_required_version\nAdd required_version."

    monkeypatch.setattr("utilities.ai.prompt.extract_tflint_guides", retrieve_guides)
    monkeypatch.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda current_event, paths_to_files: [("demo/broken/backend.tf", DEMO_BROKEN_MAIN_TF_FILE)]
    )

    prompt = make_prompt_block_with_errors_and_files(event, log_file_text_tflint)

    assert "Add required_version." in prompt
    assert prompt.index("Add required_version.") < prompt.index("File content on:")
    assert "terraform_required_version.md" in retrieved_errors[0]


def test_make_prompt_block_with_tflint_guides_disabled(
        patched_environment, monkeypatch, log_file_text_tflint, webhook_event_command_bot_list_github):
    from config import config
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files

    event = webhook_event_command_bot_list_github
    event["metadata"]["tool_name"] = "tflint"
    patched_environment.setattr(config, "rag_enabled", False)
    monkeypatch.setattr(
        "utilities.ai.prompt.extract_tflint_guides",
        lambda errors: (_ for _ in ()).throw(AssertionError("retrieval should be disabled"))
    )
    monkeypatch.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda current_event, paths_to_files: []
    )

    prompt = make_prompt_block_with_errors_and_files(event, log_file_text_tflint)

    assert "Add required_version." not in prompt


def test_make_prompt_block_with_checkov_guides_when_rag_enabled(
        patched_environment, monkeypatch, log_file_text_checkov, webhook_event_command_bot_list_github):
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files

    event = webhook_event_command_bot_list_github
    event["metadata"]["tool_name"] = "checkov"
    retrieved_errors = []

    def retrieve_guides(errors):
        retrieved_errors.append(errors)
        return "https://docs.prismacloud.io/checkov-guide\nRestrict public ingress."

    monkeypatch.setattr("utilities.ai.prompt.extract_checkov_guides", retrieve_guides)
    monkeypatch.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda current_event, paths_to_files: [("demo/broken/main.tf", DEMO_BROKEN_MAIN_TF_FILE)]
    )

    prompt = make_prompt_block_with_errors_and_files(event, log_file_text_checkov)

    assert "Restrict public ingress." in prompt
    assert prompt.index("Restrict public ingress.") < prompt.index("File content on:")
    assert "https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies" in retrieved_errors[0]


def test_make_prompt_block_with_checkov_guides_disabled(
        patched_environment, monkeypatch, log_file_text_checkov, webhook_event_command_bot_list_github):
    from config import config
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files

    event = webhook_event_command_bot_list_github
    event["metadata"]["tool_name"] = "checkov"
    patched_environment.setattr(config, "rag_enabled", False)
    monkeypatch.setattr(
        "utilities.ai.prompt.extract_checkov_guides",
        lambda errors: (_ for _ in ()).throw(AssertionError("retrieval should be disabled"))
    )
    monkeypatch.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda current_event, paths_to_files: []
    )

    prompt = make_prompt_block_with_errors_and_files(event, log_file_text_checkov)

    assert "Restrict public ingress." not in prompt


def test_make_prompt_block_with_trivy_guides_when_rag_enabled(
        patched_environment, monkeypatch, log_file_text_trivy, webhook_event_command_bot_list_github):
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files

    event = webhook_event_command_bot_list_github
    event["metadata"]["tool_name"] = "trivy"
    monkeypatch.setattr(
        "utilities.ai.prompt.extract_trivy_guides",
        lambda errors: "Guide: https://avd.aquasec.com/misconfig/aws/ec2/aws-0104\nTerraform example"
    )
    monkeypatch.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda current_event, paths_to_files: [("demo/broken/main.tf", DEMO_BROKEN_MAIN_TF_FILE)]
    )

    prompt = make_prompt_block_with_errors_and_files(event, log_file_text_trivy)

    assert "Guide: https://avd.aquasec.com/misconfig/aws/ec2/aws-0104" in prompt
    assert prompt.index("Terraform example") < prompt.index("File content on:")


def test_make_prompt_block_with_trivy_guides_disabled(
        patched_environment, monkeypatch, log_file_text_trivy, webhook_event_command_bot_list_github):
    from config import config
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files

    event = webhook_event_command_bot_list_github
    event["metadata"]["tool_name"] = "trivy"
    patched_environment.setattr(config, "rag_enabled", False)
    monkeypatch.setattr(
        "utilities.ai.prompt.extract_trivy_guides",
        lambda errors: (_ for _ in ()).throw(AssertionError("retrieval should be disabled"))
    )
    monkeypatch.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda current_event, paths_to_files: []
    )

    prompt = make_prompt_block_with_errors_and_files(event, log_file_text_trivy)

    assert "Guide:" not in prompt


def test_make_prompt_block_with_tfsec_guide_when_rag_enabled(
        patched_environment, monkeypatch, log_file_text_tfsec, webhook_event_command_bot_list_github):
    from config import config
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files

    event = webhook_event_command_bot_list_github
    event["metadata"]["tool_name"] = "tfsec"
    patched_environment.setattr(config, "rag_enabled", True)
    retrieved_errors = []

    def retrieve_guide(errors):
        retrieved_errors.append(errors)
        return "Guide: https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-acls/"

    monkeypatch.setattr("utilities.ai.prompt.extract_tfsec_guide", retrieve_guide)
    monkeypatch.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda current_event, paths_to_files: []
    )

    prompt = make_prompt_block_with_errors_and_files(event, log_file_text_tfsec)

    assert "Guide: https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-acls/" in prompt
    assert "https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-acls/" in retrieved_errors[1]
