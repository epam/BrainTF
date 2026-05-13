#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
#set -x  # Print commands and their arguments as they are executed

# Input arguments
VCS_PROVIDER="$(echo "${1}" | xargs | tr -d '\r\n')"   # Specify VCS provider: "gitlab" or "github"
ACTION="$(echo "${2}" | xargs)"                        # Specify action: "both", "post"
LOG_FILE_PATH="$(echo "${3}" | xargs)"                 # Path to the log file (e.g., log for S3)
LOG_NAME="$(echo "${4}" | xargs)"                      # Log file name (e.g., terraform-validate.log)
AWS_S3_BUCKET="$(echo "${5}" | xargs | sed 's:/*$::')" # The S3 bucket name
BASE_REPO_NAME="$(echo "${6}" | xargs)"                # Repository name (optional, for metadata)
BASE_REPO_OWNER="$(echo "${7}" | xargs)"               # Repository owner (optional, for metadata)
HEAD_BRANCH_NAME="$(echo "${8}" | xargs)"              # Branch name (optional, for metadata)
COMMIT_SHA="$(echo "${9}" | xargs)"                    # Commit SHA (optional, for metadata)
JOB_TOKEN="$(echo "${10}" | xargs)"                    # VCS job token (optional, for MR/PR comments)
PROJECT_ID_OR_REPOSITORY="$(echo "${11}" | xargs)"     # Project ID for GitLab or Repository (owner/repo) for GitHub
PIPELINE_ID_OR_RUN_ID="$(echo "${12}" | xargs)"        # Pipeline ID for GitLab or Run ID for GitHub
MR_OR_PR_NUMBER="$(echo "${13}" | xargs)"              # Merge Request IID for GitLab or Pull Request number for GitHub
OIDC_ROLE_ARN="$(echo "${14}" | xargs)"                # OIDC role ARN (optional, for AWS authentication)
VCS_OIDC_TOKEN="$(echo "${15}" | xargs)"               # OIDC token (optional, for AWS authentication)
TOOL_NAME="$(echo "${16}" | xargs)"                    # Tool name (e.g., TFLint)
PLAIN_TEXT_LOG_FILE="$(echo "${17}" | xargs)"          # Plain text log file
JOB_URL="$(echo "${18}" | xargs)"                      # Job URL for linking console logs

# Validate VCS_PROVIDER
if [ "$VCS_PROVIDER" != "gitlab" ] && [ "$VCS_PROVIDER" != "github" ]; then
  echo -e "\033[31mError: Unsupported VCS_PROVIDER value: $VCS_PROVIDER. Must be 'gitlab' or 'github'.\033[0m"
  exit 1
fi

# Check if PLAIN_TEXT_LOG_FILE exists and read its content
if [ -f "$PLAIN_TEXT_LOG_FILE" ]; then
  PLAIN_TEXT_LOG=$(<"$PLAIN_TEXT_LOG_FILE")
else
  echo -e "\033[31mError: File '$PLAIN_TEXT_LOG_FILE' does not exist.\033[0m"
  exit 1
fi

# Authenticate with AWS using OIDC if action includes upload and bucket is defined
if [ "$ACTION" != "post" ] && [ -n "$AWS_S3_BUCKET" ]; then
  # Authenticate with AWS using OIDC
  if [ "$VCS_PROVIDER" = "gitlab" ] && [ -n "$OIDC_ROLE_ARN" ] && [ -n "$VCS_OIDC_TOKEN" ]; then
    echo -e "\033[34mAuthenticating with AWS using OIDC...\033[0m"
    set +x # Disable command echoing to hide sensitive data
    aws_sts_output=$(aws sts assume-role-with-web-identity \
      --role-arn "${OIDC_ROLE_ARN}" \
      --role-session-name "VCSRunner-${CI_PROJECT_ID}-${CI_PIPELINE_ID}" \
      --web-identity-token "${VCS_OIDC_TOKEN}" \
      --duration-seconds 3600 \
      --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
      --output text) || { echo -e "\033[31mFailed to assume role with OIDC.\033[0m"; exit 1; }

    # Export AWS credentials to environment variables
    export AWS_ACCESS_KEY_ID=$(echo "$aws_sts_output" | awk '{print $1}')
    export AWS_SECRET_ACCESS_KEY=$(echo "$aws_sts_output" | awk '{print $2}')
    export AWS_SESSION_TOKEN=$(echo "$aws_sts_output" | awk '{print $3}')

    # Indicate that credentials have been successfully set
    echo -e "\033[32mAWS credentials have been successfully obtained and added to the environment.\033[0m"

    # Verify AWS credentials by calling sts get-caller-identity
    echo -e "\033[34mValidating AWS credentials...\033[0m"
    aws sts get-caller-identity || { echo -e "\033[31mFailed to validate AWS credentials.\033[0m"; exit 1; }
  fi
  # Upload log file to S3
  echo -e "\033[34mUploading $LOG_NAME to S3 bucket $AWS_S3_BUCKET in folder $MR_OR_PR_NUMBER...\033[0m"
  aws s3 cp "$LOG_FILE_PATH" "s3://$AWS_S3_BUCKET/$MR_OR_PR_NUMBER/$LOG_NAME" \
    --metadata "PULL_NUM=$MR_OR_PR_NUMBER,BASE_REPO_NAME=$BASE_REPO_NAME,BASE_REPO_OWNER=$BASE_REPO_OWNER,HEAD_BRANCH_NAME=$HEAD_BRANCH_NAME,TOOL_NAME=$TOOL_NAME,COMMIT_SHA=${COMMIT_SHA}" || {
    echo -e "\033[31mError: Failed to upload log to S3.\033[0m"
    exit 1
  }
  echo -e "\033[34mLog uploaded to S3 successfully.\033[0m"
else
  echo -e "\033[34mSkipping S3 upload (ACTION='$ACTION').\033[0m"
fi

# Check if PLAIN_TEXT_LOG_FILE exists and read its content
if [ -z "${VCS_API_ENDPOINT:-}" ]; then
  echo -e "\033[31mError: VCS_API_ENDPOINT is not set.\033[0m"
  exit 1
fi

COMMIT_AUTHOR=""
  # Determine API endpoint based on VCS_PROVIDER
if [ "$VCS_PROVIDER" = "gitlab" ]; then
  COMMENTS_URL="${VCS_API_ENDPOINT}/projects/${PROJECT_ID_OR_REPOSITORY}/merge_requests/${MR_OR_PR_NUMBER}/notes"
  AUTH_HEADER="PRIVATE-TOKEN: $JOB_TOKEN"
  COMMIT_AUTHOR="${CI_COMMIT_AUTHOR:-}"
elif [ "$VCS_PROVIDER" = "github" ]; then
  MR_OR_PR_NUMBER=$(echo "$PROJECT_ID_OR_REPOSITORY" | cut -d'/' -f3)
  COMMENTS_URL="${VCS_API_ENDPOINT}/repos/${BASE_REPO_NAME}/issues/${MR_OR_PR_NUMBER}/comments"
  AUTH_HEADER="Authorization: Bearer $JOB_TOKEN"
  COMMIT_AUTHOR="${GITHUB_ACTOR:-}"
else
  echo -e "\033[31mError: Unsupported VCS_PROVIDER value: $VCS_PROVIDER. Must be 'gitlab' or 'github'.\033[0m"
  exit 1
fi

if [ "$ACTION" = "both" ] && [ -n "$AWS_S3_BUCKET" ]; then
  LOG_LINK_TEXT="s3://$AWS_S3_BUCKET/$MR_OR_PR_NUMBER/$LOG_NAME"
  else
  LOG_LINK_TEXT="No log uploaded to S3"
fi

COMMENT_BODY=$(cat <<EOF

  :arrow_up: Job message

  ---

  The analysis process is complete for $TOOL_NAME stage

  ---

  <details><summary>Show utility outputs</summary>

  \`\`\`bash
  $PLAIN_TEXT_LOG
  \`\`\`

  </details>

  ___

  <details><summary>Show job details</summary>

  - **Job Name:** $TOOL_NAME
  - **Merge/Pull Request Number:** $MR_OR_PR_NUMBER
  - **Commit SHA:** $COMMIT_SHA
  - **Commit Author:** $COMMIT_AUTHOR
  - **Log file:** $LOG_LINK_TEXT
  - **Console Logs:** [View the job log]($JOB_URL)

  </details>
EOF
)

# Post comment to the VCS provider (GitHub or GitLab)
if [ "$VCS_PROVIDER" = "gitlab" ]; then
  echo -e "\033[34mPosting job comment to GitLab MR $MR_OR_PR_NUMBER...\033[0m"
  HTTP_CODE=$(curl -L -s -o /dev/null -w "%{http_code}" -X POST \
    -H "$AUTH_HEADER" \
    --data-urlencode "body=$COMMENT_BODY" \
    "$COMMENTS_URL")

elif [ "$VCS_PROVIDER" = "github" ]; then
  echo -e "\033[34mPosting job comment to GitHub PR $MR_OR_PR_NUMBER...\033[0m"
  COMMENT_BODY_JSON=$(jq -n --arg body "$COMMENT_BODY" '{"body": $body}')
  HTTP_CODE=$(curl -L -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "$AUTH_HEADER" \
    -H "Content-Type: application/json" \
    -d "$COMMENT_BODY_JSON" \
    "$COMMENTS_URL")
else
  echo -e "\033[33mSkipping comment as the log is empty.\033[0m"
fi

if [ "$HTTP_CODE" -ne 201 ]; then
  echo -e "\033[31mError: Failed to post comment to $VCS_PROVIDER. HTTP status code: $HTTP_CODE\033[0m"
  exit 1
else
  echo -e "\033[32mComment posted to $VCS_PROVIDER successfully.\033[0m"
fi
