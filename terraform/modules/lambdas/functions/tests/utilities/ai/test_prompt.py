from tests.data.file_samples import DEMO_BROKEN_MAIN_TF_FILE
from tests.data.logs_s3 import LOG_TEXT_TFLINT_NEW


def test_make_prompt_block_with_errors_and_files_tflint(patched_environment):
    from utilities.ai.prompt import make_prompt_block_with_errors_and_files
    event = {"metadata": {"tool_name": "checkov"}}
    patched_environment.setattr("utilities.ai.prompt.config.rag_enabled", True)
    patched_environment.setattr(
        "utilities.ai.prompt.get_all_tf_files_from_paths_list",
        lambda event, paths_to_files: [("demo/broken/main.tf", DEMO_BROKEN_MAIN_TF_FILE)],
    )
    prompt = make_prompt_block_with_errors_and_files(event, LOG_TEXT_TFLINT_NEW)
