from config import config

match config.vcs_provider:
    case "gitlab":
        from utilities.vcs.gitlab_functions import post_gitlab_comment as post_comment
        from utilities.vcs.gitlab_functions import post_help_message_gitlab as post_help_message
        from utilities.vcs.gitlab_functions import add_award_to_note_gitlab as add_award_to_note
        from utilities.vcs.gitlab_functions import check_files_exist_in_repo_gitlab as check_files_exist_in_repo
        from utilities.vcs.gitlab_functions import commit_files_to_branch_gitlab as commit_files_to_branch
        from utilities.vcs.gitlab_functions import \
            get_all_tf_files_from_paths_list_gitlab as get_all_tf_files_from_paths_list

        SUCCESS = 'white_check_mark'
        FAILURE = 'rotating_light'

    case "github":
        from utilities.vcs.github_functions import post_pr_comment_github as post_comment
        from utilities.vcs.github_functions import post_help_message_github as post_help_message
        from utilities.vcs.github_functions import add_reaction_to_pr_comment_github as add_award_to_note
        from utilities.vcs.github_functions import check_files_exist_in_repo_github as check_files_exist_in_repo
        from utilities.vcs.github_functions import commit_files_to_branch_github as commit_files_to_branch
        from utilities.vcs.github_functions import get_all_tf_files_from_paths_list_github as get_all_tf_files_from_paths_list

        SUCCESS = '+1'
        FAILURE = 'confused'

    case "bitbucket":
        ...

    case _:
        raise ValueError(f"Unsupported VCS provider: {config.vcs_provider}")

__all__ = ["post_comment", "post_help_message", "add_award_to_note", "check_files_exist_in_repo", "commit_files_to_branch",
           "get_all_tf_files_from_paths_list", "SUCCESS",
           "FAILURE"]
