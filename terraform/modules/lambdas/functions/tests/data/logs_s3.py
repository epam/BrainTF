LOG_TEXT_TFLINT = \
    """
2 issue(s) found:

Warning: Missing version constraint for provider "aws" in `required_providers` (terraform_required_providers)

  on test_code/modules/dynamodb/main.tf line 1:
   1: resource "aws_dynamodb_tab" "this" {

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_providers.md

Warning: terraform "required_version" attribute is required (terraform_required_version)

  on test_code/modules/dynamodb/main.tf line 1:

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_version.md

Working Directory: test_code/modules/dynamodb

2 issue(s) found:

Warning: Missing version constraint for provider "aws" in `required_providers` (terraform_required_providers)

  on test_code/modules/s3_bucket/main.tf line 1:
   1: resource "aws_s3_bucket" "this" {

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_providers.md

Warning: terraform "required_version" attribute is required (terraform_required_version)

  on test_code/modules/s3_bucket/main.tf line 1:

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_version.md

Working Directory: test_code/modules/s3_bucket

2 issue(s) found:

Warning: terraform "required_version" attribute is required (terraform_required_version)

  on test_code/modules/ec2_instance/main.tf line 1:

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_version.md

Warning: Missing version constraint for provider "aws" in `required_providers` (terraform_required_providers)

  on test_code/modules/ec2_instance/main.tf line 15:
  15: resource "aws_security_group" "this" {

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_providers.md

Working Directory: test_code/modules/ec2_instance

"""

LOG_TEXT_TERRAFORM = \
    """
2026-02-12T17:20:30.130Z [ERROR] AttachSchemaTransformer: No resource schema available for aws_dynamodb_tabl.this
2026-02-12T17:20:30.132Z [ERROR] vertex "output.table_name" error: Reference to undeclared resource
2026-02-12T17:20:30.132Z [ERROR] vertex "output.table_name (expand)" error: Reference to undeclared resource
2026-02-12T17:20:30.347Z [ERROR] vertex "aws_dynamodb_tabl.this" error: Invalid resource type
Error: Invalid resource type

  on main.tf line 1, in resource "aws_dynamodb_tabl" "this":
   1: resource "aws_dynamodb_tabl" "this" {

The provider hashicorp/aws does not support resource type
"aws_dynamodb_tabl". Did you mean "aws_dynamodb_table"?
Error: Reference to undeclared resource

  on outputs.tf line 3, in output "table_name":
   3:   value       = aws_dynamodb_table.this.name

A managed resource "aws_dynamodb_table" "this" has not been declared in the
root module.
Working Directory: test_code/modules/dynamodb

2026-02-12T17:20:39.263Z [ERROR] AttachSchemaTransformer: No resource schema available for aws_s3_bucke.this
2026-02-12T17:20:39.264Z [ERROR] vertex "output.bucket_name" error: Reference to undeclared resource
2026-02-12T17:20:39.264Z [ERROR] vertex "output.bucket_name (expand)" error: Reference to undeclared resource
2026-02-12T17:20:39.484Z [ERROR] vertex "aws_s3_bucke.this" error: Invalid resource type
Error: Invalid resource type

  on main.tf line 1, in resource "aws_s3_bucke" "this":
   1: resource "aws_s3_bucke" "this" {

The provider hashicorp/aws does not support resource type "aws_s3_bucke".
Did you mean "aws_s3_bucket"?
Error: Reference to undeclared resource

  on outputs.tf line 3, in output "bucket_name":
   3:   value       = aws_s3_bucket.this.bucket

A managed resource "aws_s3_bucket" "this" has not been declared in the root
module.
Working Directory: test_code/modules/s3_bucket

2026-02-12T17:20:47.660Z [ERROR] AttachSchemaTransformer: No resource schema available for aws_instanc.this
2026-02-12T17:20:47.666Z [ERROR] vertex "output.public_ip" error: Reference to undeclared resource
2026-02-12T17:20:47.667Z [ERROR] vertex "output.public_ip (expand)" error: Reference to undeclared resource
2026-02-12T17:20:48.025Z [ERROR] vertex "aws_instanc.this" error: Invalid resource type
Error: Invalid resource type

  on main.tf line 1, in resource "aws_instanc" "this":
   1: resource "aws_instanc" "this" {

The provider hashicorp/aws does not support resource type "aws_instanc".
Did you mean "aws_instance"?
Error: Reference to undeclared resource

  on outputs.tf line 3, in output "public_ip":
   3:   value       = aws_instance.this.public_ip

A managed resource "aws_instance" "this" has not been declared in the root
module.
Working Directory: test_code/modules/ec2_instance

"""

LOG_TEXT_CHECKOV = \
    """
Running Checkov analysis in directory: test_code/modules/dynamodb
terraform scan results:

Passed checks: 1, Failed checks: 2, Skipped checks: 0

Check: CKV_AWS_28: "Ensure DynamoDB point in time recovery (backup) is enabled"
	FAILED for resource: aws_dynamodb_table.this
	File: /main.tf:1-15
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-6

		1  | resource "aws_dynamodb_table" "this" {
		2  |   name           = var.table_name
		3  |   billing_mode   = "PAY_PER_REQUEST"
		4  |   hash_key       = "LockID"
		5  | 
		6  |   attribute {
		7  |     name = "LockID"
		8  |     type = "S"
		9  |   }
		10 | 
		11 |   tags = {
		12 |     Environment = "Test"
		13 |     ManagedBy   = "Terraform"
		14 |   }
		15 | }
Check: CKV_AWS_119: "Ensure DynamoDB Tables are encrypted using a KMS Customer Managed CMK"
	FAILED for resource: aws_dynamodb_table.this
	File: /main.tf:1-15
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws-52

		1  | resource "aws_dynamodb_table" "this" {
		2  |   name           = var.table_name
		3  |   billing_mode   = "PAY_PER_REQUEST"
		4  |   hash_key       = "LockID"
		5  | 
		6  |   attribute {
		7  |     name = "LockID"
		8  |     type = "S"
		9  |   }
		10 | 
		11 |   tags = {
		12 |     Environment = "Test"
		13 |     ManagedBy   = "Terraform"
		14 |   }
		15 | }

Running Checkov analysis in directory: test_code/modules/s3_bucket
terraform scan results:

Passed checks: 4, Failed checks: 7, Skipped checks: 0

Check: CKV_AWS_145: "Ensure that S3 buckets are encrypted with KMS by default"
	FAILED for resource: aws_s3_bucket.this
	File: /main.tf:1-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that-s3-buckets-are-encrypted-with-kms-by-default

		1  | resource "aws_s3_bucket" "this" {
		2  |   bucket = var.bucket_name
		3  |   acl    = "private"
		4  | 
		5  |   server_side_encryption_configuration {
		6  |     rule {
		7  |       apply_server_side_encryption_by_default {
		8  |         sse_algorithm = "AES256"
		9  |       }
		10 |     }
		11 |   }
		12 | 
		13 |   tags = {
		14 |     Environment = "Test"
		15 |     ManagedBy   = "Terraform"
		16 |   }
		17 | }
Check: CKV2_AWS_62: "Ensure S3 buckets should have event notifications enabled"
	FAILED for resource: aws_s3_bucket.this
	File: /main.tf:1-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/bc-aws-2-62

		1  | resource "aws_s3_bucket" "this" {
		2  |   bucket = var.bucket_name
		3  |   acl    = "private"
		4  | 
		5  |   server_side_encryption_configuration {
		6  |     rule {
		7  |       apply_server_side_encryption_by_default {
		8  |         sse_algorithm = "AES256"
		9  |       }
		10 |     }
		11 |   }
		12 | 
		13 |   tags = {
		14 |     Environment = "Test"
		15 |     ManagedBy   = "Terraform"
		16 |   }
		17 | }
Check: CKV2_AWS_6: "Ensure that S3 bucket has a Public Access block"
	FAILED for resource: aws_s3_bucket.this
	File: /main.tf:1-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/s3-bucket-should-have-public-access-blocks-defaults-to-false-if-the-public-access-block-is-not-attached

		1  | resource "aws_s3_bucket" "this" {
		2  |   bucket = var.bucket_name
		3  |   acl    = "private"
		4  | 
		5  |   server_side_encryption_configuration {
		6  |     rule {
		7  |       apply_server_side_encryption_by_default {
		8  |         sse_algorithm = "AES256"
		9  |       }
		10 |     }
		11 |   }
		12 | 
		13 |   tags = {
		14 |     Environment = "Test"
		15 |     ManagedBy   = "Terraform"
		16 |   }
		17 | }
Check: CKV_AWS_18: "Ensure the S3 bucket has access logging enabled"
	FAILED for resource: aws_s3_bucket.this
	File: /main.tf:1-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-13-enable-logging

		1  | resource "aws_s3_bucket" "this" {
		2  |   bucket = var.bucket_name
		3  |   acl    = "private"
		4  | 
		5  |   server_side_encryption_configuration {
		6  |     rule {
		7  |       apply_server_side_encryption_by_default {
		8  |         sse_algorithm = "AES256"
		9  |       }
		10 |     }
		11 |   }
		12 | 
		13 |   tags = {
		14 |     Environment = "Test"
		15 |     ManagedBy   = "Terraform"
		16 |   }
		17 | }
Check: CKV2_AWS_61: "Ensure that an S3 bucket has a lifecycle configuration"
	FAILED for resource: aws_s3_bucket.this
	File: /main.tf:1-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/bc-aws-2-61

		1  | resource "aws_s3_bucket" "this" {
		2  |   bucket = var.bucket_name
		3  |   acl    = "private"
		4  | 
		5  |   server_side_encryption_configuration {
		6  |     rule {
		7  |       apply_server_side_encryption_by_default {
		8  |         sse_algorithm = "AES256"
		9  |       }
		10 |     }
		11 |   }
		12 | 
		13 |   tags = {
		14 |     Environment = "Test"
		15 |     ManagedBy   = "Terraform"
		16 |   }
		17 | }
Check: CKV_AWS_21: "Ensure all data stored in the S3 bucket have versioning enabled"
	FAILED for resource: aws_s3_bucket.this
	File: /main.tf:1-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-16-enable-versioning

		1  | resource "aws_s3_bucket" "this" {
		2  |   bucket = var.bucket_name
		3  |   acl    = "private"
		4  | 
		5  |   server_side_encryption_configuration {
		6  |     rule {
		7  |       apply_server_side_encryption_by_default {
		8  |         sse_algorithm = "AES256"
		9  |       }
		10 |     }
		11 |   }
		12 | 
		13 |   tags = {
		14 |     Environment = "Test"
		15 |     ManagedBy   = "Terraform"
		16 |   }
		17 | }
Check: CKV_AWS_144: "Ensure that S3 bucket has cross-region replication enabled"
	FAILED for resource: aws_s3_bucket.this
	File: /main.tf:1-17
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that-s3-bucket-has-cross-region-replication-enabled

		1  | resource "aws_s3_bucket" "this" {
		2  |   bucket = var.bucket_name
		3  |   acl    = "private"
		4  | 
		5  |   server_side_encryption_configuration {
		6  |     rule {
		7  |       apply_server_side_encryption_by_default {
		8  |         sse_algorithm = "AES256"
		9  |       }
		10 |     }
		11 |   }
		12 | 
		13 |   tags = {
		14 |     Environment = "Test"
		15 |     ManagedBy   = "Terraform"
		16 |   }
		17 | }

Running Checkov analysis in directory: test_code/modules/ec2_instance
terraform scan results:

Passed checks: 6, Failed checks: 8, Skipped checks: 0

Check: CKV_AWS_79: "Ensure Instance Metadata Service Version 1 is not enabled"
	FAILED for resource: aws_instance.this
	File: /main.tf:1-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws-general-31

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_135: "Ensure that EC2 is EBS optimized"
	FAILED for resource: aws_instance.this
	File: /main.tf:1-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that-ec2-is-ebs-optimized

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_126: "Ensure that detailed monitoring is enabled for EC2 instances"
	FAILED for resource: aws_instance.this
	File: /main.tf:1-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/ensure-that-detailed-monitoring-is-enabled-for-ec2-instances

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_8: "Ensure all data stored in the Launch configuration or instance Elastic Blocks Store is securely encrypted"
	FAILED for resource: aws_instance.this
	File: /main.tf:1-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-13

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_23: "Ensure every security group and rule has a description"
	FAILED for resource: aws_security_group.this
	File: /main.tf:15-40
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/networking-31

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

Check: CKV_AWS_382: "Ensure no security groups allow egress from 0.0.0.0:0 to port -1"
	FAILED for resource: aws_security_group.this
	File: /main.tf:15-40
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/bc-aws-382

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

Check: CKV2_AWS_41: "Ensure an IAM role is attached to EC2 instance"
	FAILED for resource: aws_instance.this
	File: /main.tf:1-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam-policies/ensure-an-iam-role-is-attached-to-ec2-instance

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV2_AWS_5: "Ensure that Security Groups are attached to another resource"
	FAILED for resource: aws_security_group.this
	File: /main.tf:15-40
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/ensure-that-security-groups-are-attached-to-ec2-instances-or-elastic-network-interfaces-enis

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

"""

LOG_TEXT_TFSEC = \
    """
Running TFSec analysis in directory: test_code/modules/dynamodb

Result #1 HIGH Table encryption is not enabled. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-15
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name           = var.table_name
    3  │   billing_mode   = "PAY_PER_REQUEST"
    4  │   hash_key       = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-enable-at-rest-encryption
      Impact Data can be freely read if compromised
  Resolution Enable encryption at rest for DAX Cluster

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-at-rest-encryption/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dax_cluster#server_side_encryption
────────────────────────────────────────────────────────────────────────────────


Result #2 MEDIUM Point-in-time recovery is not enabled. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-15
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name           = var.table_name
    3  │   billing_mode   = "PAY_PER_REQUEST"
    4  │   hash_key       = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-enable-recovery
      Impact Accidental or malicious writes and deletes can't be rolled back
  Resolution Enable point in time recovery

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-recovery/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table#point_in_time_recovery
────────────────────────────────────────────────────────────────────────────────


Result #3 LOW Table encryption does not use a customer-managed KMS key. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-15
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name           = var.table_name
    3  │   billing_mode   = "PAY_PER_REQUEST"
    4  │   hash_key       = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-table-customer-key
      Impact Using AWS managed keys does not allow for fine grained control
  Resolution Enable server side encryption with a customer managed key

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/table-customer-key/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table#server_side_encryption
────────────────────────────────────────────────────────────────────────────────


  timings
  ──────────────────────────────────────────
  disk i/o             44.172µs
  parsing              207.888µs
  adaptation           75.26µs
  checks               5.428766ms
  total                5.756086ms

  counts
  ──────────────────────────────────────────
  modules downloaded   0
  modules processed    1
  blocks processed     3
  files read           3

  results
  ──────────────────────────────────────────
  passed               0
  ignored              0
  critical             0
  high                 1
  medium               1
  low                  1

  3 potential problem(s) detected.

Running TFSec analysis in directory: test_code/modules/s3_bucket

Result #1 HIGH No public access block so not blocking public acls 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-17
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_s3_bucket" "this" {
    2  │   bucket = var.bucket_name
    3  │   acl    = "private"
    4  │ 
    5  │   server_side_encryption_configuration {
    6  │     rule {
    7  │       apply_server_side_encryption_by_default {
    8  │         sse_algorithm = "AES256"
    9  └       }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-s3-block-public-acls
      Impact PUT calls with public ACLs specified can make objects public
  Resolution Enable blocking any PUT calls with a public ACL specified

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-acls/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block#block_public_acls
────────────────────────────────────────────────────────────────────────────────


Result #2 HIGH No public access block so not blocking public policies 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-17
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_s3_bucket" "this" {
    2  │   bucket = var.bucket_name
    3  │   acl    = "private"
    4  │ 
    5  │   server_side_encryption_configuration {
    6  │     rule {
    7  │       apply_server_side_encryption_by_default {
    8  │         sse_algorithm = "AES256"
    9  └       }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-s3-block-public-policy
      Impact Users could put a policy that allows public access
  Resolution Prevent policies that allow public access being PUT

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-policy/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block#block_public_policy
────────────────────────────────────────────────────────────────────────────────


Result #3 HIGH No public access block so not ignoring public acls 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-17
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_s3_bucket" "this" {
    2  │   bucket = var.bucket_name
    3  │   acl    = "private"
    4  │ 
    5  │   server_side_encryption_configuration {
    6  │     rule {
    7  │       apply_server_side_encryption_by_default {
    8  │         sse_algorithm = "AES256"
    9  └       }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-s3-ignore-public-acls
      Impact PUT calls with public ACLs specified can make objects public
  Resolution Enable ignoring the application of public ACLs in PUT calls

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/ignore-public-acls/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block#ignore_public_acls
────────────────────────────────────────────────────────────────────────────────


Result #4 HIGH No public access block so not restricting public buckets 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-17
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_s3_bucket" "this" {
    2  │   bucket = var.bucket_name
    3  │   acl    = "private"
    4  │ 
    5  │   server_side_encryption_configuration {
    6  │     rule {
    7  │       apply_server_side_encryption_by_default {
    8  │         sse_algorithm = "AES256"
    9  └       }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-s3-no-public-buckets
      Impact Public buckets can be accessed by anyone
  Resolution Limit the access to public buckets to only the owner or AWS Services (eg; CloudFront)

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/no-public-buckets/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block#restrict_public_buckets¡
────────────────────────────────────────────────────────────────────────────────


Result #5 HIGH Bucket does not encrypt data with a customer managed key. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-17
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_s3_bucket" "this" {
    2  │   bucket = var.bucket_name
    3  │   acl    = "private"
    4  │ 
    5  │   server_side_encryption_configuration {
    6  │     rule {
    7  │       apply_server_side_encryption_by_default {
    8  │         sse_algorithm = "AES256"
    9  └       }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-s3-encryption-customer-key
      Impact Using AWS managed keys does not allow for fine grained control
  Resolution Enable encryption using customer managed keys

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/encryption-customer-key/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket#enable-default-server-side-encryption
────────────────────────────────────────────────────────────────────────────────


Result #6 MEDIUM Bucket does not have logging enabled 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-17
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_s3_bucket" "this" {
    2  │   bucket = var.bucket_name
    3  │   acl    = "private"
    4  │ 
    5  │   server_side_encryption_configuration {
    6  │     rule {
    7  │       apply_server_side_encryption_by_default {
    8  │         sse_algorithm = "AES256"
    9  └       }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-s3-enable-bucket-logging
      Impact There is no way to determine the access to this bucket
  Resolution Add a logging block to the resource to enable access logging

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/enable-bucket-logging/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket
────────────────────────────────────────────────────────────────────────────────


Result #7 MEDIUM Bucket does not have versioning enabled 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-17
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_s3_bucket" "this" {
    2  │   bucket = var.bucket_name
    3  │   acl    = "private"
    4  │ 
    5  │   server_side_encryption_configuration {
    6  │     rule {
    7  │       apply_server_side_encryption_by_default {
    8  │         sse_algorithm = "AES256"
    9  └       }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-s3-enable-versioning
      Impact Deleted or modified data would not be recoverable
  Resolution Enable versioning to protect against accidental/malicious removal or modification

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/enable-versioning/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket#versioning
────────────────────────────────────────────────────────────────────────────────


Result #8 LOW Bucket does not have a corresponding public access block. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-17
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_s3_bucket" "this" {
    2  │   bucket = var.bucket_name
    3  │   acl    = "private"
    4  │ 
    5  │   server_side_encryption_configuration {
    6  │     rule {
    7  │       apply_server_side_encryption_by_default {
    8  │         sse_algorithm = "AES256"
    9  └       }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-s3-specify-public-access-block
      Impact Public access policies may be applied to sensitive data buckets
  Resolution Define a aws_s3_bucket_public_access_block for the given bucket to control public access policies

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/specify-public-access-block/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block#bucket
────────────────────────────────────────────────────────────────────────────────


  timings
  ──────────────────────────────────────────
  disk i/o             42.038µs
  parsing              177.432µs
  adaptation           83.285µs
  checks               11.550311ms
  total                11.853066ms

  counts
  ──────────────────────────────────────────
  modules downloaded   0
  modules processed    1
  blocks processed     3
  files read           3

  results
  ──────────────────────────────────────────
  passed               2
  ignored              0
  critical             0
  high                 5
  medium               2
  low                  1

  2 passed, 8 potential problem(s) detected.

Running TFSec analysis in directory: test_code/modules/ec2_instance

Result #1 CRITICAL Security group rule allows egress to multiple public internet addresses. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:38
────────────────────────────────────────────────────────────────────────────────
   15    resource "aws_security_group" "this" {
   ..  
   38  [     cidr_blocks = ["0.0.0.0/0"]
   ..  
   40    }
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-no-public-egress-sgr
      Impact Your port is egressing data to the internet
  Resolution Set a more restrictive cidr range

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/no-public-egress-sgr/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
────────────────────────────────────────────────────────────────────────────────


Result #2 HIGH Instance does not require IMDS access to require a token 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-12
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_instance" "this" {
    2  │   ami           = var.ami_id
    3  │   instance_type = var.instance_type
    4  │   # key_name      = var.key_name
    5  │ 
    6  │   tags = {
    7  │     Name        = var.instance_name
    8  │     Environment = "Test"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-enforce-http-token-imds
      Impact Instance metadata service can be interacted with freely
  Resolution Enable HTTP token requirement for IMDS

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enforce-http-token-imds/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#metadata-options
────────────────────────────────────────────────────────────────────────────────


Result #3 HIGH Root block device is not encrypted. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-12
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_instance" "this" {
    2  │   ami           = var.ami_id
    3  │   instance_type = var.instance_type
    4  │   # key_name      = var.key_name
    5  │ 
    6  │   tags = {
    7  │     Name        = var.instance_name
    8  │     Environment = "Test"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-enable-at-rest-encryption
      Impact The block device could be compromised and read from
  Resolution Turn on encryption for all block devices

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enable-at-rest-encryption/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#ebs-ephemeral-and-root-block-devices
────────────────────────────────────────────────────────────────────────────────


Result #4 LOW Security group rule does not have a description. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:34-39
────────────────────────────────────────────────────────────────────────────────
   15    resource "aws_security_group" "this" {
   ..  
   34  ┌   egress {
   35  │     from_port   = 0
   36  │     to_port     = 0
   37  │     protocol    = "-1"
   38  │     cidr_blocks = ["0.0.0.0/0"]
   39  └   }
   40    }
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-add-description-to-security-group-rule
      Impact Descriptions provide context for the firewall rule reasons
  Resolution Add descriptions for all security groups rules

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/add-description-to-security-group-rule/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
────────────────────────────────────────────────────────────────────────────────


  timings
  ──────────────────────────────────────────
  disk i/o             44.934µs
  parsing              303.547µs
  adaptation           92.152µs
  checks               16.441024ms
  total                16.881657ms

  counts
  ──────────────────────────────────────────
  modules downloaded   0
  modules processed    1
  blocks processed     9
  files read           3

  results
  ──────────────────────────────────────────
  passed               2
  ignored              0
  critical             1
  high                 2
  medium               0
  low                  1

  2 passed, 4 potential problem(s) detected.

"""

LOG_TEXT_SINGLE_DIR_CHECKOV = \
    """
Running Checkov analysis in directory: test_code/
Issues found in directory: test_code/.
terraform scan results:

Passed checks: 13, Failed checks: 16, Skipped checks: 0, Parsing errors: 1

Check: CKV_AWS_135: "Ensure that EC2 is EBS optimized"
	FAILED for resource: module.ec2_instance.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Calling File: /main.tf:43-51
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that-ec2-is-ebs-optimized

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_8: "Ensure all data stored in the Launch configuration or instance Elastic Blocks Store is securely encrypted"
	FAILED for resource: module.ec2_instance.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Calling File: /main.tf:43-51
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-13

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_126: "Ensure that detailed monitoring is enabled for EC2 instances"
	FAILED for resource: module.ec2_instance.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Calling File: /main.tf:43-51
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/ensure-that-detailed-monitoring-is-enabled-for-ec2-instances

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_79: "Ensure Instance Metadata Service Version 1 is not enabled"
	FAILED for resource: module.ec2_instance.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Calling File: /main.tf:43-51
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws-general-31

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_382: "Ensure no security groups allow egress from 0.0.0.0:0 to port -1"
	FAILED for resource: module.ec2_instance.aws_security_group.this
	File: /modules/ec2_instance/main.tf:15-40
	Calling File: /main.tf:43-51
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/bc-aws-382

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

Check: CKV_AWS_23: "Ensure every security group and rule has a description"
	FAILED for resource: module.ec2_instance.aws_security_group.this
	File: /modules/ec2_instance/main.tf:15-40
	Calling File: /main.tf:43-51
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/networking-31

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

Check: CKV_AWS_135: "Ensure that EC2 is EBS optimized"
	FAILED for resource: module.key_pair.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Calling File: /main.tf:24-28
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that-ec2-is-ebs-optimized

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_8: "Ensure all data stored in the Launch configuration or instance Elastic Blocks Store is securely encrypted"
	FAILED for resource: module.key_pair.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Calling File: /main.tf:24-28
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-13

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_126: "Ensure that detailed monitoring is enabled for EC2 instances"
	FAILED for resource: module.key_pair.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Calling File: /main.tf:24-28
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/ensure-that-detailed-monitoring-is-enabled-for-ec2-instances

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_79: "Ensure Instance Metadata Service Version 1 is not enabled"
	FAILED for resource: module.key_pair.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Calling File: /main.tf:24-28
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws-general-31

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV_AWS_382: "Ensure no security groups allow egress from 0.0.0.0:0 to port -1"
	FAILED for resource: module.key_pair.aws_security_group.this
	File: /modules/ec2_instance/main.tf:15-40
	Calling File: /main.tf:24-28
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/bc-aws-382

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

Check: CKV_AWS_23: "Ensure every security group and rule has a description"
	FAILED for resource: module.key_pair.aws_security_group.this
	File: /modules/ec2_instance/main.tf:15-40
	Calling File: /main.tf:24-28
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/networking-31

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

Check: CKV2_AWS_5: "Ensure that Security Groups are attached to another resource"
	FAILED for resource: module.ec2_instance.aws_security_group.this
	File: /modules/ec2_instance/main.tf:15-40
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/ensure-that-security-groups-are-attached-to-ec2-instances-or-elastic-network-interfaces-enis

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

Check: CKV2_AWS_5: "Ensure that Security Groups are attached to another resource"
	FAILED for resource: module.key_pair.aws_security_group.this
	File: /modules/ec2_instance/main.tf:15-40
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/ensure-that-security-groups-are-attached-to-ec2-instances-or-elastic-network-interfaces-enis

		15 | resource "aws_security_group" "this" {
		16 |   name        = "ec2-sg-${var.instance_name}"
		17 |   description = "Allow SSH and HTTP access"
		18 |   vpc_id      = var.vpc_id
		19 | 
		20 |   # ingress {
		21 |   #   from_port   = 22
		22 |   #   to_port     = 22
		23 |   #   protocol    = "tcp"
		24 |   #   cidr_blocks = ["0.0.0.0/0"]
		25 |   # }
		26 |   #
		27 |   # ingress {
		28 |   #   from_port   = 80
		29 |   #   to_port     = 80
		30 |   #   protocol    = "tcp"
		31 |   #   cidr_blocks = ["0.0.0.0/0"]
		32 |   # }
		33 | 
		34 |   egress {
		35 |     from_port   = 0
		36 |     to_port     = 0
		37 |     protocol    = "-1"
		38 |     cidr_blocks = ["0.0.0.0/0"]
		39 |   }
		40 | }

Check: CKV2_AWS_41: "Ensure an IAM role is attached to EC2 instance"
	FAILED for resource: module.ec2_instance.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam-policies/ensure-an-iam-role-is-attached-to-ec2-instance

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

Check: CKV2_AWS_41: "Ensure an IAM role is attached to EC2 instance"
	FAILED for resource: module.key_pair.aws_instance.this
	File: /modules/ec2_instance/main.tf:1-12
	Guide: https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam-policies/ensure-an-iam-role-is-attached-to-ec2-instance

		1  | resource "aws_instance" "this" {
		2  |   ami           = var.ami_id
		3  |   instance_type = var.instance_type
		4  |   # key_name      = var.key_name
		5  | 
		6  |   tags = {
		7  |     Name        = var.instance_name
		8  |     Environment = "Test"
		9  |   }
		10 | 
		11 |   vpc_security_group_ids = var.security_groups
		12 | }

"""

LOG_TEXT_SINGLE_DIR_TFLINT = \
    """
Failed to load configurations; test_code/modules/dynamodb/main.tf:1,36-37: Unclosed configuration block; There is no closing brace for this block before the end of the file. This may be caused by incorrect brace nesting elsewhere in this file.:

Error: Unclosed configuration block

  on test_code/modules/dynamodb/main.tf line 1, in resource "aws_dynamodb_tab" "this":
   1: resource "aws_dynamodb_tab" "this" {

There is no closing brace for this block before the end of the file. This may be caused by incorrect brace nesting elsewhere in this file.

Working Directory: test_code/modules/dynamodb

2 issue(s) found:

Warning: terraform "required_version" attribute is required (terraform_required_version)

  on test_code/modules/ec2_instance/main.tf line 1:

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_version.md

Warning: Missing version constraint for provider "aws" in `required_providers` (terraform_required_providers)

  on test_code/modules/ec2_instance/main.tf line 15:
  15: resource "aws_security_group" "this" {

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules/terraform_required_providers.md

Working Directory: test_code/modules/ec2_instance
"""

LOG_TEXT_SINGLE_DIR_TFSEC = \
    """
Running TFSec analysis in directory: test_code/
Issues found in directory: test_code/.

Results #1-2 CRITICAL Security group rule allows egress to multiple public internet addresses. (2 similar results)
────────────────────────────────────────────────────────────────────────────────
  modules/ec2_instance/main.tf:38
   via main.tf:43-51 (module.ec2_instance)
────────────────────────────────────────────────────────────────────────────────
   15    resource "aws_security_group" "this" {
   ..  
   38  [     cidr_blocks = ["0.0.0.0/0"]
   ..  
   40    }
────────────────────────────────────────────────────────────────────────────────
  Individual Causes
  - modules/ec2_instance/main.tf:43-51 (module.ec2_instance)
  - modules/ec2_instance/main.tf:24-28 (module.key_pair)
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-no-public-egress-sgr
      Impact Your port is egressing data to the internet
  Resolution Set a more restrictive cidr range

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/no-public-egress-sgr/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
────────────────────────────────────────────────────────────────────────────────


Result #3 HIGH Table encryption is not enabled. 
────────────────────────────────────────────────────────────────────────────────
  modules/dynamodb/main.tf:1-16
   via main.tf:37-40 (module.dynamodb)
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name         = var.table_name
    3  │   billing_mode = "PAY_PER_REQUEST"
    4  │   hash_key     = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └ 
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-enable-at-rest-encryption
      Impact Data can be freely read if compromised
  Resolution Enable encryption at rest for DAX Cluster

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-at-rest-encryption/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dax_cluster#server_side_encryption
────────────────────────────────────────────────────────────────────────────────


Results #4-5 HIGH Instance does not require IMDS access to require a token (2 similar results)
────────────────────────────────────────────────────────────────────────────────
  modules/ec2_instance/main.tf:1-12
   via main.tf:43-51 (module.ec2_instance)
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_instance" "this" {
    2  │   ami           = var.ami_id
    3  │   instance_type = var.instance_type
    4  │   # key_name      = var.key_name
    5  │ 
    6  │   tags = {
    7  │     Name        = var.instance_name
    8  │     Environment = "Test"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
  Individual Causes
  - modules/ec2_instance/main.tf:43-51 (module.ec2_instance)
  - modules/ec2_instance/main.tf:24-28 (module.key_pair)
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-enforce-http-token-imds
      Impact Instance metadata service can be interacted with freely
  Resolution Enable HTTP token requirement for IMDS

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enforce-http-token-imds/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#metadata-options
────────────────────────────────────────────────────────────────────────────────


Results #6-7 HIGH Root block device is not encrypted. (2 similar results)
────────────────────────────────────────────────────────────────────────────────
  modules/ec2_instance/main.tf:1-12
   via main.tf:43-51 (module.ec2_instance)
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_instance" "this" {
    2  │   ami           = var.ami_id
    3  │   instance_type = var.instance_type
    4  │   # key_name      = var.key_name
    5  │ 
    6  │   tags = {
    7  │     Name        = var.instance_name
    8  │     Environment = "Test"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
  Individual Causes
  - modules/ec2_instance/main.tf:43-51 (module.ec2_instance)
  - modules/ec2_instance/main.tf:24-28 (module.key_pair)
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-enable-at-rest-encryption
      Impact The block device could be compromised and read from
  Resolution Turn on encryption for all block devices

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enable-at-rest-encryption/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#ebs-ephemeral-and-root-block-devices
────────────────────────────────────────────────────────────────────────────────


Result #8 MEDIUM Point-in-time recovery is not enabled. 
────────────────────────────────────────────────────────────────────────────────
  modules/dynamodb/main.tf:1-16
   via main.tf:37-40 (module.dynamodb)
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name         = var.table_name
    3  │   billing_mode = "PAY_PER_REQUEST"
    4  │   hash_key     = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └ 
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-enable-recovery
      Impact Accidental or malicious writes and deletes can't be rolled back
  Resolution Enable point in time recovery

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-recovery/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table#point_in_time_recovery
────────────────────────────────────────────────────────────────────────────────


Result #9 LOW Table encryption does not use a customer-managed KMS key. 
────────────────────────────────────────────────────────────────────────────────
  modules/dynamodb/main.tf:1-16
   via main.tf:37-40 (module.dynamodb)
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name         = var.table_name
    3  │   billing_mode = "PAY_PER_REQUEST"
    4  │   hash_key     = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └ 
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-table-customer-key
      Impact Using AWS managed keys does not allow for fine grained control
  Resolution Enable server side encryption with a customer managed key

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/table-customer-key/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table#server_side_encryption
────────────────────────────────────────────────────────────────────────────────


Results #10-11 LOW Security group rule does not have a description. (2 similar results)
────────────────────────────────────────────────────────────────────────────────
  modules/ec2_instance/main.tf:34-39
   via main.tf:24-28 (module.key_pair)
────────────────────────────────────────────────────────────────────────────────
   15    resource "aws_security_group" "this" {
   ..  
   34  ┌   egress {
   35  │     from_port   = 0
   36  │     to_port     = 0
   37  │     protocol    = "-1"
   38  │     cidr_blocks = ["0.0.0.0/0"]
   39  └   }
   40    }
────────────────────────────────────────────────────────────────────────────────
  Individual Causes
  - modules/ec2_instance/main.tf:24-28 (module.key_pair)
  - modules/ec2_instance/main.tf:43-51 (module.ec2_instance)
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-add-description-to-security-group-rule
      Impact Descriptions provide context for the firewall rule reasons
  Resolution Add descriptions for all security groups rules

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/add-description-to-security-group-rule/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
────────────────────────────────────────────────────────────────────────────────


  timings
  ──────────────────────────────────────────
  disk i/o             128.74µs
  parsing              3.372568ms
  adaptation           143.907µs
  checks               2.549856ms
  total                6.195071ms

  counts
  ──────────────────────────────────────────
  modules downloaded   0
  modules processed    5
  blocks processed     34
  files read           15

  results
  ──────────────────────────────────────────
  passed               4
  ignored              0
  critical             2
  high                 5
  medium               1
  low                  3

  4 passed, 11 potential problem(s) detected.

"""

LOG_TEXT_NO_ISSUES_DIR_TFSEC = \
    """
Running TFSec analysis in directory: test_code/modules/ec2_instance
Issues found in directory: test_code/modules/ec2_instance.

Result #1 CRITICAL Security group rule allows egress to multiple public internet addresses. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:38
────────────────────────────────────────────────────────────────────────────────
   15    resource "aws_security_group" "this" {
   ..  
   38  [     cidr_blocks = ["0.0.0.0/0"]
   ..  
   40    }
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-no-public-egress-sgr
      Impact Your port is egressing data to the internet
  Resolution Set a more restrictive cidr range

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/no-public-egress-sgr/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
────────────────────────────────────────────────────────────────────────────────


Result #2 HIGH Instance does not require IMDS access to require a token 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-12
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_instance" "this" {
    2  │   ami           = var.ami_id
    3  │   instance_type = var.instance_type
    4  │   # key_name      = var.key_name
    5  │ 
    6  │   tags = {
    7  │     Name        = var.instance_name
    8  │     Environment = "Test"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-enforce-http-token-imds
      Impact Instance metadata service can be interacted with freely
  Resolution Enable HTTP token requirement for IMDS

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enforce-http-token-imds/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#metadata-options
────────────────────────────────────────────────────────────────────────────────


Result #3 HIGH Root block device is not encrypted. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-12
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_instance" "this" {
    2  │   ami           = var.ami_id
    3  │   instance_type = var.instance_type
    4  │   # key_name      = var.key_name
    5  │ 
    6  │   tags = {
    7  │     Name        = var.instance_name
    8  │     Environment = "Test"
    9  └   }
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-enable-at-rest-encryption
      Impact The block device could be compromised and read from
  Resolution Turn on encryption for all block devices

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enable-at-rest-encryption/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#ebs-ephemeral-and-root-block-devices
────────────────────────────────────────────────────────────────────────────────


Result #4 LOW Security group rule does not have a description. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:34-39
────────────────────────────────────────────────────────────────────────────────
   15    resource "aws_security_group" "this" {
   ..  
   34  ┌   egress {
   35  │     from_port   = 0
   36  │     to_port     = 0
   37  │     protocol    = "-1"
   38  │     cidr_blocks = ["0.0.0.0/0"]
   39  └   }
   40    }
────────────────────────────────────────────────────────────────────────────────
          ID aws-ec2-add-description-to-security-group-rule
      Impact Descriptions provide context for the firewall rule reasons
  Resolution Add descriptions for all security groups rules

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/add-description-to-security-group-rule/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule
────────────────────────────────────────────────────────────────────────────────


  timings
  ──────────────────────────────────────────
  disk i/o             37.901µs
  parsing              319.85µs
  adaptation           95.798µs
  checks               5.942618ms
  total                6.396167ms

  counts
  ──────────────────────────────────────────
  modules downloaded   0
  modules processed    1
  blocks processed     6
  files read           3

  results
  ──────────────────────────────────────────
  passed               2
  ignored              0
  critical             1
  high                 2
  medium               0
  low                  1

  2 passed, 4 potential problem(s) detected.

Running TFSec analysis in directory: test_code/modules/s3_bucket
No issues were found during TFSec analysis in the directory: test_code/modules/s3_bucket.
Running TFSec analysis in directory: test_code/modules/dynamodb
Issues found in directory: test_code/modules/dynamodb.

Result #1 HIGH Table encryption is not enabled. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-16
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name         = var.table_name
    3  │   billing_mode = "PAY_PER_REQUEST"
    4  │   hash_key     = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └ 
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-enable-at-rest-encryption
      Impact Data can be freely read if compromised
  Resolution Enable encryption at rest for DAX Cluster

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-at-rest-encryption/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dax_cluster#server_side_encryption
────────────────────────────────────────────────────────────────────────────────


Result #2 MEDIUM Point-in-time recovery is not enabled. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-16
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name         = var.table_name
    3  │   billing_mode = "PAY_PER_REQUEST"
    4  │   hash_key     = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └ 
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-enable-recovery
      Impact Accidental or malicious writes and deletes can't be rolled back
  Resolution Enable point in time recovery

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-recovery/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table#point_in_time_recovery
────────────────────────────────────────────────────────────────────────────────


Result #3 LOW Table encryption does not use a customer-managed KMS key. 
────────────────────────────────────────────────────────────────────────────────
  main.tf:1-16
────────────────────────────────────────────────────────────────────────────────
    1  ┌ resource "aws_dynamodb_table" "this" {
    2  │   name         = var.table_name
    3  │   billing_mode = "PAY_PER_REQUEST"
    4  │   hash_key     = "LockID"
    5  │ 
    6  │   attribute {
    7  │     name = "LockID"
    8  │     type = "S"
    9  └ 
   ..  
────────────────────────────────────────────────────────────────────────────────
          ID aws-dynamodb-table-customer-key
      Impact Using AWS managed keys does not allow for fine grained control
  Resolution Enable server side encryption with a customer managed key

  More Information
  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/table-customer-key/
  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table#server_side_encryption
────────────────────────────────────────────────────────────────────────────────


  timings
  ──────────────────────────────────────────
  disk i/o             34.983µs
  parsing              210.207µs
  adaptation           80.59µs
  checks               3.066296ms
  total                3.392076ms

  counts
  ──────────────────────────────────────────
  modules downloaded   0
  modules processed    1
  blocks processed     3
  files read           3

  results
  ──────────────────────────────────────────
  passed               0
  ignored              0
  critical             0
  high                 1
  medium               1
  low                  1

  3 potential problem(s) detected.

""".lstrip().removesuffix("\n")
