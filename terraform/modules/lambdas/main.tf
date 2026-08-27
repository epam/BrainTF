#======================= The Lambda function for AI Handler =======================#
locals {
  # Path to the functions directory
  layer_path    = "${path.module}/functions"
  zip_file_path = "${path.module}/functions/layer.zip" # Path to the output ZIP file
  # Patterns to exclude from Lambda deployment package
  lambda_exclude_patterns = [
    "!.*\\.pyc$",
    "!.*/__pycache__/.*",
    "!.*/__pycache__$",
    "!.*/\\.pytest_cache/.*",
    "!.*/\\.pytest_cache$"
  ]
}

# Install Python dependencies (replaces `docker run` in null_resource)
resource "docker_container" "lambda_layer" {
  count    = var.ai_handler_create == "true" ? 1 : 0
  name     = "braintf-${var.vcs_repo_name}-lambda-layer"
  image    = "public.ecr.aws/sam/build-python3.11:latest"
  attach   = true
  must_run = false
  command = [
    "/bin/sh",
    "-c",
    "pip install --no-cache-dir -q -r requirements.txt -t python/lib/python3.11/site-packages/ && zip -m -q -r layer.zip python"
  ]

  volumes {
    host_path      = abspath(local.layer_path)
    container_path = "/var/task"
  }
}

# Create a zip file from requirements.txt. Triggers only when the file is updated or ZIP file is missing
resource "null_resource" "lambda_layer" {
  count      = var.ai_handler_create == "true" ? 1 : 0
  depends_on = [docker_container.lambda_layer]
  triggers = {
    # Trigger when requirements.txt changes
    requirements = filesha1("${path.module}/functions/requirements.txt")
  }
  provisioner "local-exec" {
    command = <<EOT
    echo "Creating ZIP file..."
    cd ${local.layer_path}
    zip -m -q -r layer.zip python || echo "No files found to zip"
    echo "ZIP command completed."
    EOT
  }
}

# Create a new Lambda Layer Version
resource "aws_lambda_layer_version" "layer" {
  count    = var.ai_handler_create == "true" ? 1 : 0
  filename = local.zip_file_path
  # Use a static hash from null_resource triggers to avoid dynamic recalculation
  source_code_hash    = null_resource.lambda_layer[0].triggers.requirements
  layer_name          = var.layer_name
  depends_on          = [null_resource.lambda_layer] # Ensure this waits for ZIP creation
  compatible_runtimes = ["python3.11"]
}

# AWS S3 Bucket Notification for triggering Lambda functions
resource "aws_s3_bucket_notification" "bucket_notification" {
  count  = var.ai_handler_create == "true" ? 1 : 0
  bucket = var.artifacts_bucket
  lambda_function {
    lambda_function_arn = module.ai_lambda_vcs[count.index].lambda_function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "logs/"
    filter_suffix       = ".log"
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}

# Allow S3 to invoke Lambda
resource "aws_lambda_permission" "allow_bucket" {
  count         = var.ai_handler_create == "true" ? 1 : 0
  statement_id  = "AllowS3BucketToInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.ai_lambda_vcs[count.index].lambda_function_arn
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.artifacts_bucket}"
}

# AWS Lambda Function URL for vcs webhooks
resource "aws_lambda_function_url" "webhook_url_vcs" {
  count              = var.ai_handler_create == "true" ? 1 : 0
  function_name      = module.process_comment_lambda_vcs[count.index].lambda_function_name
  authorization_type = "NONE"
}

# AI Handler Lambda function for Terraform error handling
module "ai_lambda_vcs" {
  count           = var.ai_handler_create == "true" ? 1 : 0
  source          = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=4cfa5b42d1928afbc8946393e36eeee77eca0851"
  description     = "AI Handler for Terraform error handling for the ${var.vcs_repo_name} repository"
  function_name   = "AI_Handler_TF_Errors_${var.vcs_repo_name}"
  handler         = "ai_handler_tf_errors_lambda.lambda_handler"
  runtime         = "python3.11"
  timeout         = 420
  memory_size     = 256
  create_role     = false
  lambda_role     = var.lambda_exec_role_arn
  layers          = length(aws_lambda_layer_version.layer) > 0 ? [aws_lambda_layer_version.layer[0].arn] : []
  kms_key_arn     = var.kms_key_arn
  build_in_docker = true
  create_function = true
  publish         = true

  # Include only necessary directories for the comments handler
  source_path = [
    {
      path          = "${path.module}/functions/ai_handler_tf_errors_lambda" # Main directory for the errors handler
      prefix_in_zip = "/"
      patterns      = local.lambda_exclude_patterns
    },
    {
      path          = "${path.module}/functions/config.py" # The config.py for the comments handler
      prefix_in_zip = "/"
    },
    {
      path          = "${path.module}/functions/utilities" # Include AI utilities
      prefix_in_zip = "utilities"
      patterns      = local.lambda_exclude_patterns
    }
  ]

  # Environment variables specific to the comments handler
  environment_variables = {
    VCS_TOKEN_NAME      = var.vcs_token_name
    VCS_API_ENDPOINT    = var.vcs_api_endpoint
    VCS_PROVIDER        = var.vcs_provider
    WEBHOOK_SECRET_NAME = var.webhook_secret_name
    AI_API_TOKEN_NAME   = var.ai_api_token_name
    AI_API_BASE_URL     = var.ai_api_base_url
    ARTIFACTS_BUCKET    = var.artifacts_bucket
    ARTIFACTS_PATH      = var.artifacts_path
    DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    LLM_MODEL           = var.llm_model
    LOG_LEVEL           = var.log_level
    RAG_ENABLED         = var.rag_enable
  }
  tracing_mode           = "Active"
  vpc_subnet_ids         = var.private_subnet_ids
  vpc_security_group_ids = var.security_groups
  tags                   = var.tags
}

# Lambda function for processing comments in VCS PR/MR
module "process_comment_lambda_vcs" {
  count           = var.ai_handler_create == "true" ? 1 : 0
  source          = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=4cfa5b42d1928afbc8946393e36eeee77eca0851"
  description     = "AI Handler for processing comments in Git MR"
  function_name   = "AI_Handler_Comment_${var.vcs_repo_name}"
  handler         = "ai_handler_comment_lambda.lambda_handler"
  runtime         = "python3.11"
  timeout         = 420
  memory_size     = 256
  create_role     = false
  lambda_role     = var.lambda_exec_role_arn
  layers          = length(aws_lambda_layer_version.layer) > 0 ? [aws_lambda_layer_version.layer[0].arn] : []
  kms_key_arn     = var.kms_key_arn
  build_in_docker = true
  create_function = true
  publish         = true

  # Include only necessary directories for the Terraform errors handler
  source_path = [
    {
      path          = "${path.module}/functions/ai_handler_comment_lambda" # Main directory for the comments handler
      prefix_in_zip = "/"
      patterns      = local.lambda_exclude_patterns
    },
    {
      path          = "${path.module}/functions/config.py" # The config.py for the comments handler
      prefix_in_zip = "/"
    },
    {
      path          = "${path.module}/functions/utilities" # Include AI utilities
      prefix_in_zip = "utilities"
      patterns      = local.lambda_exclude_patterns
    }
  ]

  # Environment variables specific to the Terraform errors handler
  environment_variables = {
    VCS_TOKEN_NAME      = var.vcs_token_name
    VCS_API_ENDPOINT    = var.vcs_api_endpoint
    VCS_PROVIDER        = var.vcs_provider
    WEBHOOK_SECRET_NAME = var.webhook_secret_name
    AI_API_TOKEN_NAME   = var.ai_api_token_name
    AI_API_BASE_URL     = var.ai_api_base_url
    ARTIFACTS_BUCKET    = var.artifacts_bucket
    ARTIFACTS_PATH      = var.artifacts_path
    DYNAMODB_TABLE_NAME = var.dynamodb_table_name
    LLM_MODEL           = var.llm_model
    LOG_LEVEL           = var.log_level
  }
  tracing_mode           = "Active"
  vpc_subnet_ids         = var.private_subnet_ids
  vpc_security_group_ids = var.security_groups
  tags                   = var.tags
}
