import pytest

from tests.data.logs_s3 import (LOG_TEXT_CHECKOV, LOG_TEXT_TERRAFORM,
                                LOG_TEXT_TFLINT, LOG_TEXT_TFSEC, LOG_TEXT_SINGLE_DIR_TFLINT,
                                LOG_TEXT_NO_ISSUES_DIR_TFSEC)

EXTRACTED_BLOCKS_TFLINT = [('test_code/modules/dynamodb',
                            '2 issue(s) found:\n\nWarning: Missing version constraint for provider "aws" in '
                            '`required_providers` (terraform_required_providers)\n\n  on '
                            'test_code/modules/dynamodb/main.tf line 1:\n   1: resource "aws_dynamodb_tab" "this" {'
                            '\n\nReference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11'
                            '.0/docs/rules/terraform_required_providers.md\n\nWarning: terraform "required_version" '
                            'attribute is required (terraform_required_version)\n\n  on '
                            'test_code/modules/dynamodb/main.tf line 1:\n\nReference: '
                            'https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules'
                            '/terraform_required_version.md'),
                           ('test_code/modules/s3_bucket',
                            '2 issue(s) found:\n\nWarning: Missing version constraint for provider "aws" in '
                            '`required_providers` (terraform_required_providers)\n\n  on '
                            'test_code/modules/s3_bucket/main.tf line 1:\n   1: resource "aws_s3_bucket" "this" {'
                            '\n\nReference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11'
                            '.0/docs/rules/terraform_required_providers.md\n\nWarning: terraform "required_version" '
                            'attribute is required (terraform_required_version)\n\n  on '
                            'test_code/modules/s3_bucket/main.tf line 1:\n\nReference: '
                            'https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules'
                            '/terraform_required_version.md'),
                           ('test_code/modules/ec2_instance',
                            '2 issue(s) found:\n\nWarning: terraform "required_version" attribute is required ('
                            'terraform_required_version)\n\n  on test_code/modules/ec2_instance/main.tf line '
                            '1:\n\nReference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0'
                            '.11.0/docs/rules/terraform_required_version.md\n\nWarning: Missing version constraint '
                            'for provider "aws" in `required_providers` (terraform_required_providers)\n\n  on '
                            'test_code/modules/ec2_instance/main.tf line 15:\n  15: resource "aws_security_group" '
                            '"this" {\n\nReference: '
                            'https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.11.0/docs/rules'
                            '/terraform_required_providers.md')]

EXTRACTED_BLOCKS_CHECKOV = [('test_code/modules/dynamodb',
                             'terraform scan results:\n\nPassed checks: 1, Failed checks: 2, Skipped checks: '
                             '0\n\nCheck: CKV_AWS_28: "Ensure DynamoDB point in time recovery (backup) is '
                             'enabled"\n\tFAILED for resource: aws_dynamodb_table.this\n\tFile: '
                             '/main.tf:1-15\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-general-policies/general-6\n\n\t\t1  | resource "aws_dynamodb_table" "this" {\n\t\t2  '
                             '|   name           = var.table_name\n\t\t3  |   billing_mode   = '
                             '"PAY_PER_REQUEST"\n\t\t4  |   hash_key       = "LockID"\n\t\t5  | \n\t\t6  |   '
                             'attribute {\n\t\t7  |     name = "LockID"\n\t\t8  |     type = "S"\n\t\t9  |   '
                             '}\n\t\t10 | \n\t\t11 |   tags = {\n\t\t12 |     Environment = "Test"\n\t\t13 |     '
                             'ManagedBy   = "Terraform"\n\t\t14 |   }\n\t\t15 | }\nCheck: CKV_AWS_119: "Ensure '
                             'DynamoDB Tables are encrypted using a KMS Customer Managed CMK"\n\tFAILED for resource: '
                             'aws_dynamodb_table.this\n\tFile: /main.tf:1-15\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-general-policies/bc-aws-52\n\n\t\t1  | resource "aws_dynamodb_table" "this" {\n\t\t2  '
                             '|   name           = var.table_name\n\t\t3  |   billing_mode   = '
                             '"PAY_PER_REQUEST"\n\t\t4  |   hash_key       = "LockID"\n\t\t5  | \n\t\t6  |   '
                             'attribute {\n\t\t7  |     name = "LockID"\n\t\t8  |     type = "S"\n\t\t9  |   '
                             '}\n\t\t10 | \n\t\t11 |   tags = {\n\t\t12 |     Environment = "Test"\n\t\t13 |     '
                             'ManagedBy   = "Terraform"\n\t\t14 |   }\n\t\t15 | }'),
                            ('test_code/modules/s3_bucket',
                             'terraform scan results:\n\nPassed checks: 4, Failed checks: 7, Skipped checks: '
                             '0\n\nCheck: CKV_AWS_145: "Ensure that S3 buckets are encrypted with KMS by '
                             'default"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: /main.tf:1-17\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-general-policies/ensure-that-s3-buckets-are-encrypted-with-kms-by-default\n\n\t\t1  | '
                             'resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket = var.bucket_name\n\t\t3  |   acl  '
                             '  = "private"\n\t\t4  | \n\t\t5  |   server_side_encryption_configuration {\n\t\t6  |   '
                             '  rule {\n\t\t7  |       apply_server_side_encryption_by_default {\n\t\t8  |         '
                             'sse_algorithm = "AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | '
                             '\n\t\t13 |   tags = {\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   = '
                             '"Terraform"\n\t\t16 |   }\n\t\t17 | }\nCheck: CKV2_AWS_62: "Ensure S3 buckets should '
                             'have event notifications enabled"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: '
                             '/main.tf:1-17\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-logging-policies/bc-aws-2-62\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |   '
                             'bucket = var.bucket_name\n\t\t3  |   acl    = "private"\n\t\t4  | \n\t\t5  |   '
                             'server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
                             'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = '
                             '"AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = '
                             '{\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   = "Terraform"\n\t\t16 |  '
                             ' }\n\t\t17 | }\nCheck: CKV2_AWS_6: "Ensure that S3 bucket has a Public Access '
                             'block"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: /main.tf:1-17\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-networking-policies/s3-bucket-should-have-public-access-blocks-defaults-to-false-if'
                             '-the-public-access-block-is-not-attached\n\n\t\t1  | resource "aws_s3_bucket" "this" {'
                             '\n\t\t2  |   bucket = var.bucket_name\n\t\t3  |   acl    = "private"\n\t\t4  | \n\t\t5  '
                             '|   server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
                             'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = '
                             '"AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = '
                             '{\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   = "Terraform"\n\t\t16 |  '
                             ' }\n\t\t17 | }\nCheck: CKV_AWS_18: "Ensure the S3 bucket has access logging '
                             'enabled"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: /main.tf:1-17\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3'
                             '-policies/s3-13-enable-logging\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |  '
                             ' bucket = var.bucket_name\n\t\t3  |   acl    = "private"\n\t\t4  | \n\t\t5  |   '
                             'server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
                             'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = '
                             '"AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = '
                             '{\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   = "Terraform"\n\t\t16 |  '
                             ' }\n\t\t17 | }\nCheck: CKV2_AWS_61: "Ensure that an S3 bucket has a lifecycle '
                             'configuration"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: '
                             '/main.tf:1-17\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-logging-policies/bc-aws-2-61\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |   '
                             'bucket = var.bucket_name\n\t\t3  |   acl    = "private"\n\t\t4  | \n\t\t5  |   '
                             'server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
                             'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = '
                             '"AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = '
                             '{\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   = "Terraform"\n\t\t16 |  '
                             ' }\n\t\t17 | }\nCheck: CKV_AWS_21: "Ensure all data stored in the S3 bucket have '
                             'versioning enabled"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: '
                             '/main.tf:1-17\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3'
                             '-policies/s3-16-enable-versioning\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  '
                             '|   bucket = var.bucket_name\n\t\t3  |   acl    = "private"\n\t\t4  | \n\t\t5  |   '
                             'server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
                             'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = '
                             '"AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = '
                             '{\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   = "Terraform"\n\t\t16 |  '
                             ' }\n\t\t17 | }\nCheck: CKV_AWS_144: "Ensure that S3 bucket has cross-region replication '
                             'enabled"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: /main.tf:1-17\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-general-policies/ensure-that-s3-bucket-has-cross-region-replication-enabled\n\n\t\t1  '
                             '| resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket = var.bucket_name\n\t\t3  |   '
                             'acl    = "private"\n\t\t4  | \n\t\t5  |   server_side_encryption_configuration {\n\t\t6 '
                             ' |     rule {\n\t\t7  |       apply_server_side_encryption_by_default {\n\t\t8  |       '
                             '  sse_algorithm = "AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | '
                             '\n\t\t13 |   tags = {\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   = '
                             '"Terraform"\n\t\t16 |   }\n\t\t17 | }'),
                            ('test_code/modules/ec2_instance',
                             'terraform scan results:\n\nPassed checks: 6, Failed checks: 8, Skipped checks: '
                             '0\n\nCheck: CKV_AWS_79: "Ensure Instance Metadata Service Version 1 is not '
                             'enabled"\n\tFAILED for resource: aws_instance.this\n\tFile: /main.tf:1-12\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-general-policies/bc-aws-general-31\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2 '
                             ' |   ami           = var.ami_id\n\t\t3  |   instance_type = var.instance_type\n\t\t4  | '
                             '  # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   tags = {\n\t\t7  |     Name     '
                             '   = var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   }\n\t\t10 | '
                             '\n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | }\n\nCheck: '
                             'CKV_AWS_135: "Ensure that EC2 is EBS optimized"\n\tFAILED for resource: '
                             'aws_instance.this\n\tFile: /main.tf:1-12\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-general-policies/ensure-that-ec2-is-ebs-optimized\n\n\t\t1  | resource "aws_instance" '
                             '"this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   instance_type = '
                             'var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   '
                             'tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     Environment = '
                             '"Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                             'var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_126: "Ensure that detailed monitoring '
                             'is enabled for EC2 instances"\n\tFAILED for resource: aws_instance.this\n\tFile: '
                             '/main.tf:1-12\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-logging-policies/ensure-that-detailed-monitoring-is-enabled-for-ec2-instances\n\n\t\t1 '
                             ' | resource "aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   '
                             'instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | '
                             '\n\t\t6  |   tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     '
                             'Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                             'var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_8: "Ensure all data stored in the '
                             'Launch configuration or instance Elastic Blocks Store is securely encrypted"\n\tFAILED '
                             'for resource: aws_instance.this\n\tFile: /main.tf:1-12\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-general-policies/general-13\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2  |   '
                             'ami           = var.ami_id\n\t\t3  |   instance_type = var.instance_type\n\t\t4  |   # '
                             'key_name      = var.key_name\n\t\t5  | \n\t\t6  |   tags = {\n\t\t7  |     Name        '
                             '= var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 '
                             '|   vpc_security_group_ids = var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_23: '
                             '"Ensure every security group and rule has a description"\n\tFAILED for resource: '
                             'aws_security_group.this\n\tFile: /main.tf:15-40\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-networking-policies/networking-31\n\n\t\t15 | resource "aws_security_group" "this" {'
                             '\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                             '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 |   '
                             '# ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = 22\n\t\t23 | '
                             '  #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t25 |   # '
                             '}\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   from_port   = 80\n\t\t29 |   #  '
                             ' to_port     = 80\n\t\t30 |   #   protocol    = "tcp"\n\t\t31 |   #   cidr_blocks = ['
                             '"0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | \n\t\t34 |   egress {\n\t\t35 |     from_port   '
                             '= 0\n\t\t36 |     to_port     = 0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     '
                             'cidr_blocks = ["0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV_AWS_382: "Ensure no '
                             'security groups allow egress from 0.0.0.0:0 to port -1"\n\tFAILED for resource: '
                             'aws_security_group.this\n\tFile: /main.tf:15-40\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-networking-policies/bc-aws-382\n\n\t\t15 | resource "aws_security_group" "this" {'
                             '\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                             '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 |   '
                             '# ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = 22\n\t\t23 | '
                             '  #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t25 |   # '
                             '}\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   from_port   = 80\n\t\t29 |   #  '
                             ' to_port     = 80\n\t\t30 |   #   protocol    = "tcp"\n\t\t31 |   #   cidr_blocks = ['
                             '"0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | \n\t\t34 |   egress {\n\t\t35 |     from_port   '
                             '= 0\n\t\t36 |     to_port     = 0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     '
                             'cidr_blocks = ["0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV2_AWS_41: "Ensure an '
                             'IAM role is attached to EC2 instance"\n\tFAILED for resource: '
                             'aws_instance.this\n\tFile: /main.tf:1-12\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam'
                             '-policies/ensure-an-iam-role-is-attached-to-ec2-instance\n\n\t\t1  | resource '
                             '"aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   '
                             'instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | '
                             '\n\t\t6  |   tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     '
                             'Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                             'var.security_groups\n\t\t12 | }\n\nCheck: CKV2_AWS_5: "Ensure that Security Groups are '
                             'attached to another resource"\n\tFAILED for resource: aws_security_group.this\n\tFile: '
                             '/main.tf:15-40\n\tGuide: '
                             'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                             '-networking-policies/ensure-that-security-groups-are-attached-to-ec2-instances-or'
                             '-elastic-network-interfaces-enis\n\n\t\t15 | resource "aws_security_group" "this" {'
                             '\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                             '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 |   '
                             '# ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = 22\n\t\t23 | '
                             '  #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t25 |   # '
                             '}\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   from_port   = 80\n\t\t29 |   #  '
                             ' to_port     = 80\n\t\t30 |   #   protocol    = "tcp"\n\t\t31 |   #   cidr_blocks = ['
                             '"0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | \n\t\t34 |   egress {\n\t\t35 |     from_port   '
                             '= 0\n\t\t36 |     to_port     = 0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     '
                             'cidr_blocks = ["0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }')]

EXTRACTED_BLOCKS_TFSEC = [('test_code/modules/dynamodb',
                           'Result #1 HIGH Table encryption is not enabled. '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-15\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ '
                           'resource "aws_dynamodb_table" "this" {\n    2  │   name           = var.table_name\n    3  '
                           '│   billing_mode   = "PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ \n  '
                           '  6  │   attribute {\n    7  │     name = "LockID"\n    8  │     type = "S"\n    9  └   '
                           '}\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n       '
                           '   ID aws-dynamodb-enable-at-rest-encryption\n      Impact Data can be freely read if '
                           'compromised\n  Resolution Enable encryption at rest for DAX Cluster\n\n  More '
                           'Information\n  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable'
                           '-at-rest-encryption/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dax_cluster'
                           '#server_side_encryption\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #2 MEDIUM Point-in-time recovery is not enabled. '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-15\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ '
                           'resource "aws_dynamodb_table" "this" {\n    2  │   name           = var.table_name\n    3  '
                           '│   billing_mode   = "PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ \n  '
                           '  6  │   attribute {\n    7  │     name = "LockID"\n    8  │     type = "S"\n    9  └   '
                           '}\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n       '
                           '   ID aws-dynamodb-enable-recovery\n      Impact Accidental or malicious writes and '
                           'deletes can\'t be rolled back\n  Resolution Enable point in time recovery\n\n  More '
                           'Information\n  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable'
                           '-recovery/\n  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs'
                           '/resources/dynamodb_table#point_in_time_recovery\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #3 LOW Table encryption does not use a customer-managed KMS key. '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-15\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_dynamodb_table" "this" {\n    2  │   name           = var.table_name\n    '
                           '3  │   billing_mode   = "PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ '
                           '\n    6  │   attribute {\n    7  │     name = "LockID"\n    8  │     type = "S"\n    9  └ '
                           '  }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-dynamodb-table-customer-key\n      Impact Using AWS managed keys does not '
                           'allow for fine grained control\n  Resolution Enable server side encryption with a '
                           'customer managed key\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/table-customer-key/\n  '
                           '- https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/dynamodb_table#server_side_encryption\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n\n  '
                           'timings\n  ──────────────────────────────────────────\n  disk i/o             44.172µs\n  '
                           'parsing              207.888µs\n  adaptation           75.26µs\n  checks               '
                           '5.428766ms\n  total                5.756086ms\n\n  counts\n  '
                           '──────────────────────────────────────────\n  modules downloaded   0\n  modules processed '
                           '   1\n  blocks processed     3\n  files read           3\n\n  results\n  '
                           '──────────────────────────────────────────\n  passed               0\n  ignored           '
                           '   0\n  critical             0\n  high                 1\n  medium               1\n  low '
                           '                 1\n\n  3 potential problem(s) detected.'),
                          ('test_code/modules/s3_bucket',
                           'Result #1 HIGH No public access block so not blocking public acls '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-17\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl  '
                           '  = "private"\n    4  │ \n    5  │   server_side_encryption_configuration {\n    6  │     '
                           'rule {\n    7  │       apply_server_side_encryption_by_default {\n    8  │         '
                           'sse_algorithm = "AES256"\n    9  └       }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-s3-block-public-acls\n      Impact PUT calls with public ACLs specified can '
                           'make objects public\n  Resolution Enable blocking any PUT calls with a public ACL '
                           'specified\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-acls/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/s3_bucket_public_access_block#block_public_acls\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #2 HIGH No public access block so not blocking public policies '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-17\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl  '
                           '  = "private"\n    4  │ \n    5  │   server_side_encryption_configuration {\n    6  │     '
                           'rule {\n    7  │       apply_server_side_encryption_by_default {\n    8  │         '
                           'sse_algorithm = "AES256"\n    9  └       }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-s3-block-public-policy\n      Impact Users could put a policy that allows '
                           'public access\n  Resolution Prevent policies that allow public access being PUT\n\n  More '
                           'Information\n  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public'
                           '-policy/\n  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/s3_bucket_public_access_block#block_public_policy\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #3 HIGH No public access block so not ignoring public acls '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-17\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl  '
                           '  = "private"\n    4  │ \n    5  │   server_side_encryption_configuration {\n    6  │     '
                           'rule {\n    7  │       apply_server_side_encryption_by_default {\n    8  │         '
                           'sse_algorithm = "AES256"\n    9  └       }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-s3-ignore-public-acls\n      Impact PUT calls with public ACLs specified can '
                           'make objects public\n  Resolution Enable ignoring the application of public ACLs in PUT '
                           'calls\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/ignore-public-acls/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/s3_bucket_public_access_block#ignore_public_acls\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #4 HIGH No public access block so not restricting public buckets '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-17\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl  '
                           '  = "private"\n    4  │ \n    5  │   server_side_encryption_configuration {\n    6  │     '
                           'rule {\n    7  │       apply_server_side_encryption_by_default {\n    8  │         '
                           'sse_algorithm = "AES256"\n    9  └       }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-s3-no-public-buckets\n      Impact Public buckets can be accessed by anyone\n  '
                           'Resolution Limit the access to public buckets to only the owner or AWS Services (eg; '
                           'CloudFront)\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/no-public-buckets/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/s3_bucket_public_access_block#restrict_public_buckets¡\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #5 HIGH Bucket does not encrypt data with a customer managed key. '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-17\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl  '
                           '  = "private"\n    4  │ \n    5  │   server_side_encryption_configuration {\n    6  │     '
                           'rule {\n    7  │       apply_server_side_encryption_by_default {\n    8  │         '
                           'sse_algorithm = "AES256"\n    9  └       }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-s3-encryption-customer-key\n      Impact Using AWS managed keys does not allow '
                           'for fine grained control\n  Resolution Enable encryption using customer managed keys\n\n  '
                           'More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/encryption-customer-key/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket'
                           '#enable-default-server-side-encryption\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #6 MEDIUM Bucket does not have logging enabled '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-17\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl  '
                           '  = "private"\n    4  │ \n    5  │   server_side_encryption_configuration {\n    6  │     '
                           'rule {\n    7  │       apply_server_side_encryption_by_default {\n    8  │         '
                           'sse_algorithm = "AES256"\n    9  └       }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-s3-enable-bucket-logging\n      Impact There is no way to determine the access '
                           'to this bucket\n  Resolution Add a logging block to the resource to enable access '
                           'logging\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/enable-bucket-logging/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #7 MEDIUM Bucket does not have versioning enabled '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-17\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl  '
                           '  = "private"\n    4  │ \n    5  │   server_side_encryption_configuration {\n    6  │     '
                           'rule {\n    7  │       apply_server_side_encryption_by_default {\n    8  │         '
                           'sse_algorithm = "AES256"\n    9  └       }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-s3-enable-versioning\n      Impact Deleted or modified data would not be '
                           'recoverable\n  Resolution Enable versioning to protect against accidental/malicious '
                           'removal or modification\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/enable-versioning/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket'
                           '#versioning\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #8 LOW Bucket does not have a corresponding public access block. '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-17\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl  '
                           '  = "private"\n    4  │ \n    5  │   server_side_encryption_configuration {\n    6  │     '
                           'rule {\n    7  │       apply_server_side_encryption_by_default {\n    8  │         '
                           'sse_algorithm = "AES256"\n    9  └       }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-s3-specify-public-access-block\n      Impact Public access policies may be '
                           'applied to sensitive data buckets\n  Resolution Define a '
                           'aws_s3_bucket_public_access_block for the given bucket to control public access '
                           'policies\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/specify-public-access-block'
                           '/\n  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/s3_bucket_public_access_block#bucket\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n\n  '
                           'timings\n  ──────────────────────────────────────────\n  disk i/o             42.038µs\n  '
                           'parsing              177.432µs\n  adaptation           83.285µs\n  checks               '
                           '11.550311ms\n  total                11.853066ms\n\n  counts\n  '
                           '──────────────────────────────────────────\n  modules downloaded   0\n  modules processed '
                           '   1\n  blocks processed     3\n  files read           3\n\n  results\n  '
                           '──────────────────────────────────────────\n  passed               2\n  ignored           '
                           '   0\n  critical             0\n  high                 5\n  medium               2\n  low '
                           '                 1\n\n  2 passed, 8 potential problem(s) detected.'),
                          ('test_code/modules/ec2_instance',
                           'Result #1 CRITICAL Security group rule allows egress to multiple public internet '
                           'addresses. '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:38\n'
                           '────────────────────────────────────────────────────────────────────────────────\n   15   '
                           ' resource "aws_security_group" "this" {\n   ..  \n   38  [     cidr_blocks = ['
                           '"0.0.0.0/0"]\n   ..  \n   40    '
                           '}\n────────────────────────────────────────────────────────────────────────────────\n     '
                           '     ID aws-ec2-no-public-egress-sgr\n      Impact Your port is egressing data to the '
                           'internet\n  Resolution Set a more restrictive cidr range\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/no-public-egress-sgr/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/security_group\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #2 HIGH Instance does not require IMDS access to require a token '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-12\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_instance" "this" {\n    2  │   ami           = var.ami_id\n    3  │   '
                           'instance_type = var.instance_type\n    4  │   # key_name      = var.key_name\n    5  │ \n '
                           '   6  │   tags = {\n    7  │     Name        = var.instance_name\n    8  │     '
                           'Environment = "Test"\n    9  └   }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-ec2-enforce-http-token-imds\n      Impact Instance metadata service can be '
                           'interacted with freely\n  Resolution Enable HTTP token requirement for IMDS\n\n  More '
                           'Information\n  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enforce'
                           '-http-token-imds/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance'
                           '#metadata-options\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #3 HIGH Root block device is not encrypted. '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:1-12\n'
                           '────────────────────────────────────────────────────────────────────────────────\n    1  '
                           '┌ resource "aws_instance" "this" {\n    2  │   ami           = var.ami_id\n    3  │   '
                           'instance_type = var.instance_type\n    4  │   # key_name      = var.key_name\n    5  │ \n '
                           '   6  │   tags = {\n    7  │     Name        = var.instance_name\n    8  │     '
                           'Environment = "Test"\n    9  └   }\n   ..  '
                           '\n────────────────────────────────────────────────────────────────────────────────\n      '
                           '    ID aws-ec2-enable-at-rest-encryption\n      Impact The block device could be '
                           'compromised and read from\n  Resolution Turn on encryption for all block devices\n\n  '
                           'More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enable-at-rest-encryption/\n '
                           ' - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance'
                           '#ebs-ephemeral-and-root-block-devices\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n'
                           '\nResult #4 LOW Security group rule does not have a description. '
                           '\n────────────────────────────────────────────────────────────────────────────────\n  '
                           'main.tf:34-39\n'
                           '────────────────────────────────────────────────────────────────────────────────\n   15   '
                           ' resource "aws_security_group" "this" {\n   ..  \n   34  ┌   egress {\n   35  │     '
                           'from_port   = 0\n   36  │     to_port     = 0\n   37  │     protocol    = "-1"\n   38  │  '
                           '   cidr_blocks = ["0.0.0.0/0"]\n   39  └   }\n   40    '
                           '}\n────────────────────────────────────────────────────────────────────────────────\n     '
                           '     ID aws-ec2-add-description-to-security-group-rule\n      Impact Descriptions provide '
                           'context for the firewall rule reasons\n  Resolution Add descriptions for all security '
                           'groups rules\n\n  More Information\n  - '
                           'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/add-description-to-security'
                           '-group-rule/\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/security_group\n  - '
                           'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
                           '/security_group_rule\n'
                           '────────────────────────────────────────────────────────────────────────────────\n\n\n  '
                           'timings\n  ──────────────────────────────────────────\n  disk i/o             44.934µs\n  '
                           'parsing              303.547µs\n  adaptation           92.152µs\n  checks               '
                           '16.441024ms\n  total                16.881657ms\n\n  counts\n  '
                           '──────────────────────────────────────────\n  modules downloaded   0\n  modules processed '
                           '   1\n  blocks processed     9\n  files read           3\n\n  results\n  '
                           '──────────────────────────────────────────\n  passed               2\n  ignored           '
                           '   0\n  critical             1\n  high                 2\n  medium               0\n  low '
                           '                 1\n\n  2 passed, 4 potential problem(s) detected.')]

EXTRACTED_BLOCKS_TERRAFORM = [('test_code/modules/dynamodb',
                               '2026-02-12T17:20:30.130Z [ERROR] AttachSchemaTransformer: No resource '
                               'schema available for aws_dynamodb_tabl.this\n'
                               '2026-02-12T17:20:30.132Z [ERROR] vertex "output.table_name" error: '
                               'Reference to undeclared resource\n'
                               '2026-02-12T17:20:30.132Z [ERROR] vertex "output.table_name (expand)" error: '
                               'Reference to undeclared resource\n'
                               '2026-02-12T17:20:30.347Z [ERROR] vertex "aws_dynamodb_tabl.this" error: '
                               'Invalid resource type\n'
                               'Error: Invalid resource type\n'
                               '\n'
                               '  on main.tf line 1, in resource "aws_dynamodb_tabl" "this":\n'
                               '   1: resource "aws_dynamodb_tabl" "this" {\n'
                               '\n'
                               'The provider hashicorp/aws does not support resource type\n'
                               '"aws_dynamodb_tabl". Did you mean "aws_dynamodb_table"?\n'
                               'Error: Reference to undeclared resource\n'
                               '\n'
                               '  on outputs.tf line 3, in output "table_name":\n'
                               '   3:   value       = aws_dynamodb_table.this.name\n'
                               '\n'
                               'A managed resource "aws_dynamodb_table" "this" has not been declared in '
                               'the\n'
                               'root module.'),
                              ('test_code/modules/s3_bucket',
                               '2026-02-12T17:20:39.263Z [ERROR] AttachSchemaTransformer: No resource '
                               'schema available for aws_s3_bucke.this\n'
                               '2026-02-12T17:20:39.264Z [ERROR] vertex "output.bucket_name" error: '
                               'Reference to undeclared resource\n'
                               '2026-02-12T17:20:39.264Z [ERROR] vertex "output.bucket_name (expand)" '
                               'error: Reference to undeclared resource\n'
                               '2026-02-12T17:20:39.484Z [ERROR] vertex "aws_s3_bucke.this" error: Invalid '
                               'resource type\n'
                               'Error: Invalid resource type\n'
                               '\n'
                               '  on main.tf line 1, in resource "aws_s3_bucke" "this":\n'
                               '   1: resource "aws_s3_bucke" "this" {\n'
                               '\n'
                               'The provider hashicorp/aws does not support resource type "aws_s3_bucke".\n'
                               'Did you mean "aws_s3_bucket"?\n'
                               'Error: Reference to undeclared resource\n'
                               '\n'
                               '  on outputs.tf line 3, in output "bucket_name":\n'
                               '   3:   value       = aws_s3_bucket.this.bucket\n'
                               '\n'
                               'A managed resource "aws_s3_bucket" "this" has not been declared in the '
                               'root\n'
                               'module.'),
                              ('test_code/modules/ec2_instance',
                               '2026-02-12T17:20:47.660Z [ERROR] AttachSchemaTransformer: No resource '
                               'schema available for aws_instanc.this\n'
                               '2026-02-12T17:20:47.666Z [ERROR] vertex "output.public_ip" error: Reference '
                               'to undeclared resource\n'
                               '2026-02-12T17:20:47.667Z [ERROR] vertex "output.public_ip (expand)" error: '
                               'Reference to undeclared resource\n'
                               '2026-02-12T17:20:48.025Z [ERROR] vertex "aws_instanc.this" error: Invalid '
                               'resource type\n'
                               'Error: Invalid resource type\n'
                               '\n'
                               '  on main.tf line 1, in resource "aws_instanc" "this":\n'
                               '   1: resource "aws_instanc" "this" {\n'
                               '\n'
                               'The provider hashicorp/aws does not support resource type "aws_instanc".\n'
                               'Did you mean "aws_instance"?\n'
                               'Error: Reference to undeclared resource\n'
                               '\n'
                               '  on outputs.tf line 3, in output "public_ip":\n'
                               '   3:   value       = aws_instance.this.public_ip\n'
                               '\n'
                               'A managed resource "aws_instance" "this" has not been declared in the root\n'
                               'module.')]

REPLACED_WORKDIR_BLOCKS_TERRAFORM = [
    '2026-02-12T17:20:30.130Z [ERROR] AttachSchemaTransformer: No resource schema available for '
    'aws_dynamodb_tabl.this\n2026-02-12T17:20:30.132Z [ERROR] vertex "output.table_name" error: Reference to '
    'undeclared resource\n2026-02-12T17:20:30.132Z [ERROR] vertex "output.table_name (expand)" error: Reference to '
    'undeclared resource\n2026-02-12T17:20:30.347Z [ERROR] vertex "aws_dynamodb_tabl.this" error: Invalid resource '
    'type\nError: Invalid resource type\n\n  on test_code/modules/dynamodb/main.tf line 1, in resource '
    '"aws_dynamodb_tabl" "this":\n   1: resource "aws_dynamodb_tabl" "this" {\n\nThe provider hashicorp/aws does not '
    'support resource type\n"aws_dynamodb_tabl". Did you mean "aws_dynamodb_table"?\nError: Reference to undeclared '
    'resource\n\n  on test_code/modules/dynamodb/outputs.tf line 3, in output "table_name":\n   3:   value       = '
    'aws_dynamodb_table.this.name\n\nA managed resource "aws_dynamodb_table" "this" has not been declared in '
    'the\nroot module.',
    '2026-02-12T17:20:39.263Z [ERROR] AttachSchemaTransformer: No resource schema available for '
    'aws_s3_bucke.this\n2026-02-12T17:20:39.264Z [ERROR] vertex "output.bucket_name" error: Reference to undeclared '
    'resource\n2026-02-12T17:20:39.264Z [ERROR] vertex "output.bucket_name (expand)" error: Reference to undeclared '
    'resource\n2026-02-12T17:20:39.484Z [ERROR] vertex "aws_s3_bucke.this" error: Invalid resource type\nError: '
    'Invalid resource type\n\n  on test_code/modules/s3_bucket/main.tf line 1, in resource "aws_s3_bucke" "this":\n   '
    '1: resource "aws_s3_bucke" "this" {\n\nThe provider hashicorp/aws does not support resource type '
    '"aws_s3_bucke".\nDid you mean "aws_s3_bucket"?\nError: Reference to undeclared resource\n\n  on '
    'test_code/modules/s3_bucket/outputs.tf line 3, in output "bucket_name":\n   3:   value       = '
    'aws_s3_bucket.this.bucket\n\nA managed resource "aws_s3_bucket" "this" has not been declared in the root\nmodule.',
    '2026-02-12T17:20:47.660Z [ERROR] AttachSchemaTransformer: No resource schema available for '
    'aws_instanc.this\n2026-02-12T17:20:47.666Z [ERROR] vertex "output.public_ip" error: Reference to undeclared '
    'resource\n2026-02-12T17:20:47.667Z [ERROR] vertex "output.public_ip (expand)" error: Reference to undeclared '
    'resource\n2026-02-12T17:20:48.025Z [ERROR] vertex "aws_instanc.this" error: Invalid resource type\nError: '
    'Invalid resource type\n\n  on test_code/modules/ec2_instance/main.tf line 1, in resource "aws_instanc" "this":\n '
    '  1: resource "aws_instanc" "this" {\n\nThe provider hashicorp/aws does not support resource type '
    '"aws_instanc".\nDid you mean "aws_instance"?\nError: Reference to undeclared resource\n\n  on '
    'test_code/modules/ec2_instance/outputs.tf line 3, in output "public_ip":\n   3:   value       = '
    'aws_instance.this.public_ip\n\nA managed resource "aws_instance" "this" has not been declared in the '
    'root\nmodule.']

REPLACED_WORKDIR_BLOCKS_TFSEC = [
    'Result #1 HIGH Table encryption is not enabled. '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/dynamodb/main.tf:1-15\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_dynamodb_table" "this" {\n    2  │   name           = var.table_name\n    3  │   billing_mode   = '
    '"PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ \n    6  │   attribute {\n    7  │     name = '
    '"LockID"\n    8  │     type = "S"\n    9  └   }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-dynamodb-enable-at-rest-encryption\n      Impact Data can be freely read if compromised\n  Resolution Enable '
    'encryption at rest for DAX Cluster\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-at-rest-encryption/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dax_cluster#server_side_encryption\n'
    '────────────────────────────────────────────────────────────────────────────────\n\n\nResult #2 MEDIUM '
    'Point-in-time recovery is not enabled. '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/dynamodb/main.tf:1-15\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_dynamodb_table" "this" {\n    2  │   name           = var.table_name\n    3  │   billing_mode   = '
    '"PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ \n    6  │   attribute {\n    7  │     name = '
    '"LockID"\n    8  │     type = "S"\n    9  └   }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-dynamodb-enable-recovery\n      Impact Accidental or malicious writes and deletes can\'t be rolled back\n  '
    'Resolution Enable point in time recovery\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/enable-recovery/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table'
    '#point_in_time_recovery\n────────────────────────────────────────────────────────────────────────────────\n\n'
    '\nResult #3 LOW Table encryption does not use a customer-managed KMS key. '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/dynamodb/main.tf:1-15\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_dynamodb_table" "this" {\n    2  │   name           = var.table_name\n    3  │   billing_mode   = '
    '"PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ \n    6  │   attribute {\n    7  │     name = '
    '"LockID"\n    8  │     type = "S"\n    9  └   }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-dynamodb-table-customer-key\n      Impact Using AWS managed keys does not allow for fine grained control\n  '
    'Resolution Enable server side encryption with a customer managed key\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/dynamodb/table-customer-key/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table'
    '#server_side_encryption\n────────────────────────────────────────────────────────────────────────────────\n\n\n  '
    'timings\n  ──────────────────────────────────────────\n  disk i/o             44.172µs\n  parsing              '
    '207.888µs\n  adaptation           75.26µs\n  checks               5.428766ms\n  total                '
    '5.756086ms\n\n  counts\n  ──────────────────────────────────────────\n  modules downloaded   0\n  modules '
    'processed    1\n  blocks processed     3\n  files read           3\n\n  results\n  '
    '──────────────────────────────────────────\n  passed               0\n  ignored              0\n  critical       '
    '      0\n  high                 1\n  medium               1\n  low                  1\n\n  3 potential problem('
    's) detected.',
    'Result #1 HIGH No public access block so not blocking public acls '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/s3_bucket/main.tf:1-17\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-s3-block-public-acls\n      Impact PUT calls with public ACLs specified can make objects public\n  '
    'Resolution Enable blocking any PUT calls with a public ACL specified\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-acls/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block'
    '#block_public_acls\n────────────────────────────────────────────────────────────────────────────────\n\n\nResult '
    '#2 HIGH No public access block so not blocking public policies '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/s3_bucket/main.tf:1-17\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-s3-block-public-policy\n      Impact Users could put a policy that allows public access\n  Resolution '
    'Prevent policies that allow public access being PUT\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/block-public-policy/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block'
    '#block_public_policy\n────────────────────────────────────────────────────────────────────────────────\n\n'
    '\nResult #3 HIGH No public access block so not ignoring public acls '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/s3_bucket/main.tf:1-17\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-s3-ignore-public-acls\n      Impact PUT calls with public ACLs specified can make objects public\n  '
    'Resolution Enable ignoring the application of public ACLs in PUT calls\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/ignore-public-acls/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block'
    '#ignore_public_acls\n────────────────────────────────────────────────────────────────────────────────\n\n'
    '\nResult #4 HIGH No public access block so not restricting public buckets '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/s3_bucket/main.tf:1-17\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-s3-no-public-buckets\n      Impact Public buckets can be accessed by anyone\n  Resolution Limit the access '
    'to public buckets to only the owner or AWS Services (eg; CloudFront)\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/no-public-buckets/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block'
    '#restrict_public_buckets¡\n────────────────────────────────────────────────────────────────────────────────\n\n'
    '\nResult #5 HIGH Bucket does not encrypt data with a customer managed key. '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/s3_bucket/main.tf:1-17\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-s3-encryption-customer-key\n      Impact Using AWS managed keys does not allow for fine grained control\n  '
    'Resolution Enable encryption using customer managed keys\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/encryption-customer-key/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket#enable-default-server-side'
    '-encryption\n────────────────────────────────────────────────────────────────────────────────\n\n\nResult #6 '
    'MEDIUM Bucket does not have logging enabled '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/s3_bucket/main.tf:1-17\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-s3-enable-bucket-logging\n      Impact There is no way to determine the access to this bucket\n  Resolution '
    'Add a logging block to the resource to enable access logging\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/enable-bucket-logging/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket\n'
    '────────────────────────────────────────────────────────────────────────────────\n\n\nResult #7 MEDIUM Bucket '
    'does not have versioning enabled '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/s3_bucket/main.tf:1-17\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-s3-enable-versioning\n      Impact Deleted or modified data would not be recoverable\n  Resolution Enable '
    'versioning to protect against accidental/malicious removal or modification\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/enable-versioning/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket#versioning\n'
    '────────────────────────────────────────────────────────────────────────────────\n\n\nResult #8 LOW Bucket does '
    'not have a corresponding public access block. '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/s3_bucket/main.tf:1-17\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-s3-specify-public-access-block\n      Impact Public access policies may be applied to sensitive data '
    'buckets\n  Resolution Define a aws_s3_bucket_public_access_block for the given bucket to control public access '
    'policies\n\n  More Information\n  - https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/s3/specify-public'
    '-access-block/\n  - https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources'
    '/s3_bucket_public_access_block#bucket\n'
    '────────────────────────────────────────────────────────────────────────────────\n\n\n  timings\n  '
    '──────────────────────────────────────────\n  disk i/o             42.038µs\n  parsing              177.432µs\n  '
    'adaptation           83.285µs\n  checks               11.550311ms\n  total                11.853066ms\n\n  '
    'counts\n  ──────────────────────────────────────────\n  modules downloaded   0\n  modules processed    1\n  '
    'blocks processed     3\n  files read           3\n\n  results\n  ──────────────────────────────────────────\n  '
    'passed               2\n  ignored              0\n  critical             0\n  high                 5\n  medium   '
    '            2\n  low                  1\n\n  2 passed, 8 potential problem(s) detected.',
    'Result #1 CRITICAL Security group rule allows egress to multiple public internet addresses. '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/ec2_instance/main.tf:38\n'
    '────────────────────────────────────────────────────────────────────────────────\n   15    resource '
    '"aws_security_group" "this" {\n   ..  \n   38  [     cidr_blocks = ["0.0.0.0/0"]\n   ..  \n   40    '
    '}\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-ec2-no-public-egress-sgr\n      Impact Your port is egressing data to the internet\n  Resolution Set a more '
    'restrictive cidr range\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/no-public-egress-sgr/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group\n'
    '────────────────────────────────────────────────────────────────────────────────\n\n\nResult #2 HIGH Instance '
    'does not require IMDS access to require a token '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/ec2_instance/main.tf:1-12\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_instance" "this" {\n    2  │   ami           = var.ami_id\n    3  │   instance_type = var.instance_type\n   '
    ' 4  │   # key_name      = var.key_name\n    5  │ \n    6  │   tags = {\n    7  │     Name        = '
    'var.instance_name\n    8  │     Environment = "Test"\n    9  └   }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-ec2-enforce-http-token-imds\n      Impact Instance metadata service can be interacted with freely\n  '
    'Resolution Enable HTTP token requirement for IMDS\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enforce-http-token-imds/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#metadata-options\n'
    '────────────────────────────────────────────────────────────────────────────────\n\n\nResult #3 HIGH Root block '
    'device is not encrypted. \n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/ec2_instance/main.tf:1-12\n'
    '────────────────────────────────────────────────────────────────────────────────\n    1  ┌ resource '
    '"aws_instance" "this" {\n    2  │   ami           = var.ami_id\n    3  │   instance_type = var.instance_type\n   '
    ' 4  │   # key_name      = var.key_name\n    5  │ \n    6  │   tags = {\n    7  │     Name        = '
    'var.instance_name\n    8  │     Environment = "Test"\n    9  └   }\n   ..  '
    '\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-ec2-enable-at-rest-encryption\n      Impact The block device could be compromised and read from\n  '
    'Resolution Turn on encryption for all block devices\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/enable-at-rest-encryption/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#ebs-ephemeral-and-root'
    '-block-devices\n────────────────────────────────────────────────────────────────────────────────\n\n\nResult #4 '
    'LOW Security group rule does not have a description. '
    '\n────────────────────────────────────────────────────────────────────────────────\n  '
    'test_code/modules/ec2_instance/main.tf:34-39\n'
    '────────────────────────────────────────────────────────────────────────────────\n   15    resource '
    '"aws_security_group" "this" {\n   ..  \n   34  ┌   egress {\n   35  │     from_port   = 0\n   36  │     to_port  '
    '   = 0\n   37  │     protocol    = "-1"\n   38  │     cidr_blocks = ["0.0.0.0/0"]\n   39  └   }\n   40    '
    '}\n────────────────────────────────────────────────────────────────────────────────\n          ID '
    'aws-ec2-add-description-to-security-group-rule\n      Impact Descriptions provide context for the firewall rule '
    'reasons\n  Resolution Add descriptions for all security groups rules\n\n  More Information\n  - '
    'https://aquasecurity.github.io/tfsec/v1.28.12/checks/aws/ec2/add-description-to-security-group-rule/\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group\n  - '
    'https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule\n'
    '────────────────────────────────────────────────────────────────────────────────\n\n\n  timings\n  '
    '──────────────────────────────────────────\n  disk i/o             44.934µs\n  parsing              303.547µs\n  '
    'adaptation           92.152µs\n  checks               16.441024ms\n  total                16.881657ms\n\n  '
    'counts\n  ──────────────────────────────────────────\n  modules downloaded   0\n  modules processed    1\n  '
    'blocks processed     9\n  files read           3\n\n  results\n  ──────────────────────────────────────────\n  '
    'passed               2\n  ignored              0\n  critical             1\n  high                 2\n  medium   '
    '            0\n  low                  1\n\n  2 passed, 4 potential problem(s) detected.']

REPLACED_WORKDIR_BLOCKS_CHECKOV = [
    'terraform scan results:\n\nPassed checks: 1, Failed checks: 2, Skipped checks: 0\n\nCheck: CKV_AWS_28: "Ensure '
    'DynamoDB point in time recovery (backup) is enabled"\n\tFAILED for resource: aws_dynamodb_table.this\n\tFile: '
    'test_code/modules/dynamodb/main.tf:1-15\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-6\n'
    '\n\t\t1  | resource "aws_dynamodb_table" "this" {\n\t\t2  |   name           = var.table_name\n\t\t3  |   '
    'billing_mode   = "PAY_PER_REQUEST"\n\t\t4  |   hash_key       = "LockID"\n\t\t5  | \n\t\t6  |   attribute {'
    '\n\t\t7  |     name = "LockID"\n\t\t8  |     type = "S"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   tags = {\n\t\t12 |  '
    '   Environment = "Test"\n\t\t13 |     ManagedBy   = "Terraform"\n\t\t14 |   }\n\t\t15 | }\nCheck: CKV_AWS_119: '
    '"Ensure DynamoDB Tables are encrypted using a KMS Customer Managed CMK"\n\tFAILED for resource: '
    'aws_dynamodb_table.this\n\tFile: test_code/modules/dynamodb/main.tf:1-15\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws-52\n'
    '\n\t\t1  | resource "aws_dynamodb_table" "this" {\n\t\t2  |   name           = var.table_name\n\t\t3  |   '
    'billing_mode   = "PAY_PER_REQUEST"\n\t\t4  |   hash_key       = "LockID"\n\t\t5  | \n\t\t6  |   attribute {'
    '\n\t\t7  |     name = "LockID"\n\t\t8  |     type = "S"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   tags = {\n\t\t12 |  '
    '   Environment = "Test"\n\t\t13 |     ManagedBy   = "Terraform"\n\t\t14 |   }\n\t\t15 | }',
    'terraform scan results:\n\nPassed checks: 4, Failed checks: 7, Skipped checks: 0\n\nCheck: CKV_AWS_145: "Ensure '
    'that S3 buckets are encrypted with KMS by default"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: '
    'test_code/modules/s3_bucket/main.tf:1-17\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that'
    '-s3-buckets-are-encrypted-with-kms-by-default\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket = '
    'var.bucket_name\n\t\t3  |   acl    = "private"\n\t\t4  | \n\t\t5  |   server_side_encryption_configuration {'
    '\n\t\t6  |     rule {\n\t\t7  |       apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm '
    '= "AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = {\n\t\t14 |     '
    'Environment = "Test"\n\t\t15 |     ManagedBy   = "Terraform"\n\t\t16 |   }\n\t\t17 | }\nCheck: CKV2_AWS_62: '
    '"Ensure S3 buckets should have event notifications enabled"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: '
    'test_code/modules/s3_bucket/main.tf:1-17\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/bc-aws-2-62'
    '\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket = var.bucket_name\n\t\t3  |   acl    = '
    '"private"\n\t\t4  | \n\t\t5  |   server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
    'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = "AES256"\n\t\t9  |       }\n\t\t10 | '
    '    }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = {\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   '
    '= "Terraform"\n\t\t16 |   }\n\t\t17 | }\nCheck: CKV2_AWS_6: "Ensure that S3 bucket has a Public Access '
    'block"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: test_code/modules/s3_bucket/main.tf:1-17\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/s3'
    '-bucket-should-have-public-access-blocks-defaults-to-false-if-the-public-access-block-is-not-attached\n\n\t\t1  '
    '| resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket = var.bucket_name\n\t\t3  |   acl    = "private"\n\t\t4  '
    '| \n\t\t5  |   server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
    'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = "AES256"\n\t\t9  |       }\n\t\t10 | '
    '    }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = {\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   '
    '= "Terraform"\n\t\t16 |   }\n\t\t17 | }\nCheck: CKV_AWS_18: "Ensure the S3 bucket has access logging '
    'enabled"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: test_code/modules/s3_bucket/main.tf:1-17\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-13-enable-logging'
    '\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket = var.bucket_name\n\t\t3  |   acl    = '
    '"private"\n\t\t4  | \n\t\t5  |   server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
    'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = "AES256"\n\t\t9  |       }\n\t\t10 | '
    '    }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = {\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   '
    '= "Terraform"\n\t\t16 |   }\n\t\t17 | }\nCheck: CKV2_AWS_61: "Ensure that an S3 bucket has a lifecycle '
    'configuration"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: '
    'test_code/modules/s3_bucket/main.tf:1-17\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/bc-aws-2-61'
    '\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket = var.bucket_name\n\t\t3  |   acl    = '
    '"private"\n\t\t4  | \n\t\t5  |   server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
    'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = "AES256"\n\t\t9  |       }\n\t\t10 | '
    '    }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = {\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   '
    '= "Terraform"\n\t\t16 |   }\n\t\t17 | }\nCheck: CKV_AWS_21: "Ensure all data stored in the S3 bucket have '
    'versioning enabled"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: '
    'test_code/modules/s3_bucket/main.tf:1-17\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-16-enable'
    '-versioning\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket = var.bucket_name\n\t\t3  |   acl   '
    ' = "private"\n\t\t4  | \n\t\t5  |   server_side_encryption_configuration {\n\t\t6  |     rule {\n\t\t7  |       '
    'apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm = "AES256"\n\t\t9  |       }\n\t\t10 | '
    '    }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = {\n\t\t14 |     Environment = "Test"\n\t\t15 |     ManagedBy   '
    '= "Terraform"\n\t\t16 |   }\n\t\t17 | }\nCheck: CKV_AWS_144: "Ensure that S3 bucket has cross-region replication '
    'enabled"\n\tFAILED for resource: aws_s3_bucket.this\n\tFile: test_code/modules/s3_bucket/main.tf:1-17\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that'
    '-s3-bucket-has-cross-region-replication-enabled\n\n\t\t1  | resource "aws_s3_bucket" "this" {\n\t\t2  |   bucket '
    '= var.bucket_name\n\t\t3  |   acl    = "private"\n\t\t4  | \n\t\t5  |   server_side_encryption_configuration {'
    '\n\t\t6  |     rule {\n\t\t7  |       apply_server_side_encryption_by_default {\n\t\t8  |         sse_algorithm '
    '= "AES256"\n\t\t9  |       }\n\t\t10 |     }\n\t\t11 |   }\n\t\t12 | \n\t\t13 |   tags = {\n\t\t14 |     '
    'Environment = "Test"\n\t\t15 |     ManagedBy   = "Terraform"\n\t\t16 |   }\n\t\t17 | }',
    'terraform scan results:\n\nPassed checks: 6, Failed checks: 8, Skipped checks: 0\n\nCheck: CKV_AWS_79: "Ensure '
    'Instance Metadata Service Version 1 is not enabled"\n\tFAILED for resource: aws_instance.this\n\tFile: '
    'test_code/modules/ec2_instance/main.tf:1-12\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/bc-aws'
    '-general-31\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   '
    'instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   tags = {'
    '\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   }\n\t\t10 | '
    '\n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_135: "Ensure that EC2 is '
    'EBS optimized"\n\tFAILED for resource: aws_instance.this\n\tFile: '
    'test_code/modules/ec2_instance/main.tf:1-12\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/ensure-that'
    '-ec2-is-ebs-optimized\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3 '
    ' |   instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   tags = '
    '{\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   }\n\t\t10 | '
    '\n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_126: "Ensure that '
    'detailed monitoring is enabled for EC2 instances"\n\tFAILED for resource: aws_instance.this\n\tFile: '
    'test_code/modules/ec2_instance/main.tf:1-12\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-logging-policies/ensure-that'
    '-detailed-monitoring-is-enabled-for-ec2-instances\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2  |   ami   '
    '        = var.ami_id\n\t\t3  |   instance_type = var.instance_type\n\t\t4  |   # key_name      = '
    'var.key_name\n\t\t5  | \n\t\t6  |   tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     '
    'Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | '
    '}\n\nCheck: CKV_AWS_8: "Ensure all data stored in the Launch configuration or instance Elastic Blocks Store is '
    'securely encrypted"\n\tFAILED for resource: aws_instance.this\n\tFile: '
    'test_code/modules/ec2_instance/main.tf:1-12\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-general-policies/general-13'
    '\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   instance_type = '
    'var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   tags = {\n\t\t7  |     Name  '
    '      = var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   '
    'vpc_security_group_ids = var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_23: "Ensure every security group and '
    'rule has a description"\n\tFAILED for resource: aws_security_group.this\n\tFile: '
    'test_code/modules/ec2_instance/main.tf:15-40\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies'
    '/networking-31\n\n\t\t15 | resource "aws_security_group" "this" {\n\t\t16 |   name        = "ec2-sg-${'
    'var.instance_name}"\n\t\t17 |   description = "Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = '
    'var.vpc_id\n\t\t19 | \n\t\t20 |   # ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = '
    '22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   '
    '#\n\t\t27 |   # ingress {\n\t\t28 |   #   from_port   = 80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   '
    'protocol    = "tcp"\n\t\t31 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | \n\t\t34 |   egress {'
    '\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port     = 0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     '
    'cidr_blocks = ["0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV_AWS_382: "Ensure no security groups allow '
    'egress from 0.0.0.0:0 to port -1"\n\tFAILED for resource: aws_security_group.this\n\tFile: '
    'test_code/modules/ec2_instance/main.tf:15-40\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/bc-aws'
    '-382\n\n\t\t15 | resource "aws_security_group" "this" {\n\t\t16 |   name        = "ec2-sg-${'
    'var.instance_name}"\n\t\t17 |   description = "Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = '
    'var.vpc_id\n\t\t19 | \n\t\t20 |   # ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = '
    '22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   '
    '#\n\t\t27 |   # ingress {\n\t\t28 |   #   from_port   = 80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   '
    'protocol    = "tcp"\n\t\t31 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | \n\t\t34 |   egress {'
    '\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port     = 0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     '
    'cidr_blocks = ["0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV2_AWS_41: "Ensure an IAM role is attached to '
    'EC2 instance"\n\tFAILED for resource: aws_instance.this\n\tFile: '
    'test_code/modules/ec2_instance/main.tf:1-12\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-iam-policies/ensure-an-iam'
    '-role-is-attached-to-ec2-instance\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2  |   ami           = '
    'var.ami_id\n\t\t3  |   instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | '
    '\n\t\t6  |   tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  | '
    '  }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | }\n\nCheck: CKV2_AWS_5: '
    '"Ensure that Security Groups are attached to another resource"\n\tFAILED for resource: '
    'aws_security_group.this\n\tFile: test_code/modules/ec2_instance/main.tf:15-40\n\tGuide: '
    'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws-networking-policies/ensure'
    '-that-security-groups-are-attached-to-ec2-instances-or-elastic-network-interfaces-enis\n\n\t\t15 | resource '
    '"aws_security_group" "this" {\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
    '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 |   # ingress {\n\t\t21 |   '
    '#   from_port   = 22\n\t\t22 |   #   to_port     = 22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   '
    'cidr_blocks = ["0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   from_port   = '
    '80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   protocol    = "tcp"\n\t\t31 |   #   cidr_blocks = ['
    '"0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | \n\t\t34 |   egress {\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port '
    '    = 0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     cidr_blocks = ["0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }']

CLEANED_ERRORS_BLOCKS_TFSEC = [
    'Result #1 HIGH Table encryption is not enabled. \n───\n  main.tf:1-15\n───\n    1  ┌ resource '
    '"aws_dynamodb_table" "this" {\n    2  │   name           = var.table_name\n    3  │   billing_mode   = '
    '"PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ \n    6  │   attribute {\n    7  │     name = '
    '"LockID"\n    8  │     type = "S"\n    9  └   }\n   ..  \n───\n          ID '
    'aws-dynamodb-enable-at-rest-encryption\n      Impact Data can be freely read if compromised\n  Resolution Enable '
    'encryption at rest for DAX Cluster\n\n\n\nResult #2 MEDIUM Point-in-time recovery is not enabled. \n───\n  '
    'main.tf:1-15\n───\n    1  ┌ resource "aws_dynamodb_table" "this" {\n    2  │   name           = var.table_name\n '
    '   3  │   billing_mode   = "PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ \n    6  │   '
    'attribute {\n    7  │     name = "LockID"\n    8  │     type = "S"\n    9  └   }\n   ..  \n───\n          ID '
    'aws-dynamodb-enable-recovery\n      Impact Accidental or malicious writes and deletes can\'t be rolled back\n  '
    'Resolution Enable point in time recovery\n\n\n\nResult #3 LOW Table encryption does not use a customer-managed '
    'KMS key. \n───\n  main.tf:1-15\n───\n    1  ┌ resource "aws_dynamodb_table" "this" {\n    2  │   name           '
    '= var.table_name\n    3  │   billing_mode   = "PAY_PER_REQUEST"\n    4  │   hash_key       = "LockID"\n    5  │ '
    '\n    6  │   attribute {\n    7  │     name = "LockID"\n    8  │     type = "S"\n    9  └   }\n   ..  \n───\n    '
    '      ID aws-dynamodb-table-customer-key\n      Impact Using AWS managed keys does not allow for fine grained '
    'control\n  Resolution Enable server side encryption with a customer managed key',
    'Result #1 HIGH No public access block so not blocking public acls \n───\n  main.tf:1-17\n───\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n───\n          ID aws-s3-block-public-acls\n      Impact PUT calls with public ACLs specified can make objects '
    'public\n  Resolution Enable blocking any PUT calls with a public ACL specified\n\n\n\nResult #2 HIGH No public '
    'access block so not blocking public policies \n───\n  main.tf:1-17\n───\n    1  ┌ resource "aws_s3_bucket" '
    '"this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  │   '
    'server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n───\n          ID aws-s3-block-public-policy\n      Impact Users could put a policy that allows public '
    'access\n  Resolution Prevent policies that allow public access being PUT\n\n\n\nResult #3 HIGH No public access '
    'block so not ignoring public acls \n───\n  main.tf:1-17\n───\n    1  ┌ resource "aws_s3_bucket" "this" {\n    2  '
    '│   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  │   '
    'server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n───\n          ID aws-s3-ignore-public-acls\n      Impact PUT calls with public ACLs specified can make '
    'objects public\n  Resolution Enable ignoring the application of public ACLs in PUT calls\n\n\n\nResult #4 HIGH '
    'No public access block so not restricting public buckets \n───\n  main.tf:1-17\n───\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n───\n          ID aws-s3-no-public-buckets\n      Impact Public buckets can be accessed by anyone\n  '
    'Resolution Limit the access to public buckets to only the owner or AWS Services (eg; CloudFront)\n\n\n\nResult '
    '#5 HIGH Bucket does not encrypt data with a customer managed key. \n───\n  main.tf:1-17\n───\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n───\n          ID aws-s3-encryption-customer-key\n      Impact Using AWS managed keys does not allow for fine '
    'grained control\n  Resolution Enable encryption using customer managed keys\n\n\n\nResult #6 MEDIUM Bucket does '
    'not have logging enabled \n───\n  main.tf:1-17\n───\n    1  ┌ resource "aws_s3_bucket" "this" {\n    2  │   '
    'bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  │   '
    'server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n───\n          ID aws-s3-enable-bucket-logging\n      Impact There is no way to determine the access to this '
    'bucket\n  Resolution Add a logging block to the resource to enable access logging\n\n\n\nResult #7 MEDIUM Bucket '
    'does not have versioning enabled \n───\n  main.tf:1-17\n───\n    1  ┌ resource "aws_s3_bucket" "this" {\n    2  '
    '│   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  │   '
    'server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n───\n          ID aws-s3-enable-versioning\n      Impact Deleted or modified data would not be recoverable\n  '
    'Resolution Enable versioning to protect against accidental/malicious removal or modification\n\n\n\nResult #8 '
    'LOW Bucket does not have a corresponding public access block. \n───\n  main.tf:1-17\n───\n    1  ┌ resource '
    '"aws_s3_bucket" "this" {\n    2  │   bucket = var.bucket_name\n    3  │   acl    = "private"\n    4  │ \n    5  '
    '│   server_side_encryption_configuration {\n    6  │     rule {\n    7  │       '
    'apply_server_side_encryption_by_default {\n    8  │         sse_algorithm = "AES256"\n    9  └       }\n   ..  '
    '\n───\n          ID aws-s3-specify-public-access-block\n      Impact Public access policies may be applied to '
    'sensitive data buckets\n  Resolution Define a aws_s3_bucket_public_access_block for the given bucket to control '
    'public access policies',
    'Result #1 CRITICAL Security group rule allows egress to multiple public internet addresses. \n───\n  '
    'main.tf:38\n───\n   15    resource "aws_security_group" "this" {\n   ..  \n   38  [     cidr_blocks = ['
    '"0.0.0.0/0"]\n   ..  \n   40    }\n───\n          ID aws-ec2-no-public-egress-sgr\n      Impact Your port is '
    'egressing data to the internet\n  Resolution Set a more restrictive cidr range\n\n\n\nResult #2 HIGH Instance '
    'does not require IMDS access to require a token \n───\n  main.tf:1-12\n───\n    1  ┌ resource "aws_instance" '
    '"this" {\n    2  │   ami           = var.ami_id\n    3  │   instance_type = var.instance_type\n    4  │   # '
    'key_name      = var.key_name\n    5  │ \n    6  │   tags = {\n    7  │     Name        = var.instance_name\n    '
    '8  │     Environment = "Test"\n    9  └   }\n   ..  \n───\n          ID aws-ec2-enforce-http-token-imds\n      '
    'Impact Instance metadata service can be interacted with freely\n  Resolution Enable HTTP token requirement for '
    'IMDS\n\n\n\nResult #3 HIGH Root block device is not encrypted. \n───\n  main.tf:1-12\n───\n    1  ┌ resource '
    '"aws_instance" "this" {\n    2  │   ami           = var.ami_id\n    3  │   instance_type = var.instance_type\n   '
    ' 4  │   # key_name      = var.key_name\n    5  │ \n    6  │   tags = {\n    7  │     Name        = '
    'var.instance_name\n    8  │     Environment = "Test"\n    9  └   }\n   ..  \n───\n          ID '
    'aws-ec2-enable-at-rest-encryption\n      Impact The block device could be compromised and read from\n  '
    'Resolution Turn on encryption for all block devices\n\n\n\nResult #4 LOW Security group rule does not have a '
    'description. \n───\n  main.tf:34-39\n───\n   15    resource "aws_security_group" "this" {\n   ..  \n   34  ┌   '
    'egress {\n   35  │     from_port   = 0\n   36  │     to_port     = 0\n   37  │     protocol    = "-1"\n   38  │  '
    '   cidr_blocks = ["0.0.0.0/0"]\n   39  └   }\n   40    }\n───\n          ID '
    'aws-ec2-add-description-to-security-group-rule\n      Impact Descriptions provide context for the firewall rule '
    'reasons\n  Resolution Add descriptions for all security groups rules']

EXTRACTED_MONO_BLOCK_CHECKOV = [('test_code/',
                                 'Issues found in directory: test_code/.\nterraform scan results:\n\nPassed checks: '
                                 '13, Failed checks: 16, Skipped checks: 0, Parsing errors: 1\n\nCheck: CKV_AWS_135: '
                                 '"Ensure that EC2 is EBS optimized"\n\tFAILED for resource: '
                                 'module.ec2_instance.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tCalling File: /main.tf:43-51\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-general-policies/ensure-that-ec2-is-ebs-optimized\n\n\t\t1  | resource '
                                 '"aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   '
                                 'instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5 '
                                 ' | \n\t\t6  |   tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |    '
                                 ' Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                                 'var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_8: "Ensure all data stored in the '
                                 'Launch configuration or instance Elastic Blocks Store is securely '
                                 'encrypted"\n\tFAILED for resource: module.ec2_instance.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tCalling File: /main.tf:43-51\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-general-policies/general-13\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2  | '
                                 '  ami           = var.ami_id\n\t\t3  |   instance_type = var.instance_type\n\t\t4  '
                                 '|   # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   tags = {\n\t\t7  |     '
                                 'Name        = var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   '
                                 '}\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | '
                                 '}\n\nCheck: CKV_AWS_126: "Ensure that detailed monitoring is enabled for EC2 '
                                 'instances"\n\tFAILED for resource: module.ec2_instance.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tCalling File: /main.tf:43-51\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-logging-policies/ensure-that-detailed-monitoring-is-enabled-for-ec2-instances\n\n'
                                 '\t\t1  | resource "aws_instance" "this" {\n\t\t2  |   ami           = '
                                 'var.ami_id\n\t\t3  |   instance_type = var.instance_type\n\t\t4  |   # key_name     '
                                 ' = var.key_name\n\t\t5  | \n\t\t6  |   tags = {\n\t\t7  |     Name        = '
                                 'var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   }\n\t\t10 | '
                                 '\n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | }\n\nCheck: '
                                 'CKV_AWS_79: "Ensure Instance Metadata Service Version 1 is not enabled"\n\tFAILED '
                                 'for resource: module.ec2_instance.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tCalling File: /main.tf:43-51\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-general-policies/bc-aws-general-31\n\n\t\t1  | resource "aws_instance" "this" {'
                                 '\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   instance_type = '
                                 'var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   '
                                 'tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     Environment = '
                                 '"Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                                 'var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_382: "Ensure no security groups '
                                 'allow egress from 0.0.0.0:0 to port -1"\n\tFAILED for resource: '
                                 'module.ec2_instance.aws_security_group.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:15-40\n\tCalling File: /main.tf:43-51\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-networking-policies/bc-aws-382\n\n\t\t15 | resource "aws_security_group" "this" {'
                                 '\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                                 '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 '
                                 '|   # ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = '
                                 '22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   '
                                 'from_port   = 80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   protocol    = '
                                 '"tcp"\n\t\t31 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | '
                                 '\n\t\t34 |   egress {\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port     = '
                                 '0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV_AWS_23: "Ensure every security '
                                 'group and rule has a description"\n\tFAILED for resource: '
                                 'module.ec2_instance.aws_security_group.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:15-40\n\tCalling File: /main.tf:43-51\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-networking-policies/networking-31\n\n\t\t15 | resource "aws_security_group" "this" '
                                 '{\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                                 '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 '
                                 '|   # ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = '
                                 '22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   '
                                 'from_port   = 80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   protocol    = '
                                 '"tcp"\n\t\t31 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | '
                                 '\n\t\t34 |   egress {\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port     = '
                                 '0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV_AWS_135: "Ensure that EC2 is '
                                 'EBS optimized"\n\tFAILED for resource: module.key_pair.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tCalling File: /main.tf:24-28\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-general-policies/ensure-that-ec2-is-ebs-optimized\n\n\t\t1  | resource '
                                 '"aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   '
                                 'instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5 '
                                 ' | \n\t\t6  |   tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |    '
                                 ' Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                                 'var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_8: "Ensure all data stored in the '
                                 'Launch configuration or instance Elastic Blocks Store is securely '
                                 'encrypted"\n\tFAILED for resource: module.key_pair.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tCalling File: /main.tf:24-28\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-general-policies/general-13\n\n\t\t1  | resource "aws_instance" "this" {\n\t\t2  | '
                                 '  ami           = var.ami_id\n\t\t3  |   instance_type = var.instance_type\n\t\t4  '
                                 '|   # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   tags = {\n\t\t7  |     '
                                 'Name        = var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   '
                                 '}\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | '
                                 '}\n\nCheck: CKV_AWS_126: "Ensure that detailed monitoring is enabled for EC2 '
                                 'instances"\n\tFAILED for resource: module.key_pair.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tCalling File: /main.tf:24-28\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-logging-policies/ensure-that-detailed-monitoring-is-enabled-for-ec2-instances\n\n'
                                 '\t\t1  | resource "aws_instance" "this" {\n\t\t2  |   ami           = '
                                 'var.ami_id\n\t\t3  |   instance_type = var.instance_type\n\t\t4  |   # key_name     '
                                 ' = var.key_name\n\t\t5  | \n\t\t6  |   tags = {\n\t\t7  |     Name        = '
                                 'var.instance_name\n\t\t8  |     Environment = "Test"\n\t\t9  |   }\n\t\t10 | '
                                 '\n\t\t11 |   vpc_security_group_ids = var.security_groups\n\t\t12 | }\n\nCheck: '
                                 'CKV_AWS_79: "Ensure Instance Metadata Service Version 1 is not enabled"\n\tFAILED '
                                 'for resource: module.key_pair.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tCalling File: /main.tf:24-28\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-general-policies/bc-aws-general-31\n\n\t\t1  | resource "aws_instance" "this" {'
                                 '\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   instance_type = '
                                 'var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5  | \n\t\t6  |   '
                                 'tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |     Environment = '
                                 '"Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                                 'var.security_groups\n\t\t12 | }\n\nCheck: CKV_AWS_382: "Ensure no security groups '
                                 'allow egress from 0.0.0.0:0 to port -1"\n\tFAILED for resource: '
                                 'module.key_pair.aws_security_group.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:15-40\n\tCalling File: /main.tf:24-28\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-networking-policies/bc-aws-382\n\n\t\t15 | resource "aws_security_group" "this" {'
                                 '\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                                 '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 '
                                 '|   # ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = '
                                 '22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   '
                                 'from_port   = 80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   protocol    = '
                                 '"tcp"\n\t\t31 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | '
                                 '\n\t\t34 |   egress {\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port     = '
                                 '0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV_AWS_23: "Ensure every security '
                                 'group and rule has a description"\n\tFAILED for resource: '
                                 'module.key_pair.aws_security_group.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:15-40\n\tCalling File: /main.tf:24-28\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-networking-policies/networking-31\n\n\t\t15 | resource "aws_security_group" "this" '
                                 '{\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                                 '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 '
                                 '|   # ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = '
                                 '22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   '
                                 'from_port   = 80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   protocol    = '
                                 '"tcp"\n\t\t31 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | '
                                 '\n\t\t34 |   egress {\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port     = '
                                 '0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV2_AWS_5: "Ensure that Security '
                                 'Groups are attached to another resource"\n\tFAILED for resource: '
                                 'module.ec2_instance.aws_security_group.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:15-40\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-networking-policies/ensure-that-security-groups-are-attached-to-ec2-instances-or'
                                 '-elastic-network-interfaces-enis\n\n\t\t15 | resource "aws_security_group" "this" {'
                                 '\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                                 '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 '
                                 '|   # ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = '
                                 '22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   '
                                 'from_port   = 80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   protocol    = '
                                 '"tcp"\n\t\t31 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | '
                                 '\n\t\t34 |   egress {\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port     = '
                                 '0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV2_AWS_5: "Ensure that Security '
                                 'Groups are attached to another resource"\n\tFAILED for resource: '
                                 'module.key_pair.aws_security_group.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:15-40\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-networking-policies/ensure-that-security-groups-are-attached-to-ec2-instances-or'
                                 '-elastic-network-interfaces-enis\n\n\t\t15 | resource "aws_security_group" "this" {'
                                 '\n\t\t16 |   name        = "ec2-sg-${var.instance_name}"\n\t\t17 |   description = '
                                 '"Allow SSH and HTTP access"\n\t\t18 |   vpc_id      = var.vpc_id\n\t\t19 | \n\t\t20 '
                                 '|   # ingress {\n\t\t21 |   #   from_port   = 22\n\t\t22 |   #   to_port     = '
                                 '22\n\t\t23 |   #   protocol    = "tcp"\n\t\t24 |   #   cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t25 |   # }\n\t\t26 |   #\n\t\t27 |   # ingress {\n\t\t28 |   #   '
                                 'from_port   = 80\n\t\t29 |   #   to_port     = 80\n\t\t30 |   #   protocol    = '
                                 '"tcp"\n\t\t31 |   #   cidr_blocks = ["0.0.0.0/0"]\n\t\t32 |   # }\n\t\t33 | '
                                 '\n\t\t34 |   egress {\n\t\t35 |     from_port   = 0\n\t\t36 |     to_port     = '
                                 '0\n\t\t37 |     protocol    = "-1"\n\t\t38 |     cidr_blocks = ['
                                 '"0.0.0.0/0"]\n\t\t39 |   }\n\t\t40 | }\n\nCheck: CKV2_AWS_41: "Ensure an IAM role '
                                 'is attached to EC2 instance"\n\tFAILED for resource: '
                                 'module.ec2_instance.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-iam-policies/ensure-an-iam-role-is-attached-to-ec2-instance\n\n\t\t1  | resource '
                                 '"aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   '
                                 'instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5 '
                                 ' | \n\t\t6  |   tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |    '
                                 ' Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                                 'var.security_groups\n\t\t12 | }\n\nCheck: CKV2_AWS_41: "Ensure an IAM role is '
                                 'attached to EC2 instance"\n\tFAILED for resource: '
                                 'module.key_pair.aws_instance.this\n\tFile: '
                                 '/modules/ec2_instance/main.tf:1-12\n\tGuide: '
                                 'https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/aws'
                                 '-iam-policies/ensure-an-iam-role-is-attached-to-ec2-instance\n\n\t\t1  | resource '
                                 '"aws_instance" "this" {\n\t\t2  |   ami           = var.ami_id\n\t\t3  |   '
                                 'instance_type = var.instance_type\n\t\t4  |   # key_name      = var.key_name\n\t\t5 '
                                 ' | \n\t\t6  |   tags = {\n\t\t7  |     Name        = var.instance_name\n\t\t8  |    '
                                 ' Environment = "Test"\n\t\t9  |   }\n\t\t10 | \n\t\t11 |   vpc_security_group_ids = '
                                 'var.security_groups\n\t\t12 | }')]

REPLACED_PATHS_MONO_BLOCK_CHECKOV = \
    """
Issues found in directory: test_code/.
terraform scan results:

Passed checks: 13, Failed checks: 16, Skipped checks: 0, Parsing errors: 1

Check: CKV_AWS_135: "Ensure that EC2 is EBS optimized"
	FAILED for resource: module.ec2_instance.aws_instance.this
	File: test_code/modules/ec2_instance/main.tf:1-12
	Calling File: test_code/main.tf:43-51
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
	File: test_code/modules/ec2_instance/main.tf:1-12
	Calling File: test_code/main.tf:43-51
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
	File: test_code/modules/ec2_instance/main.tf:1-12
	Calling File: test_code/main.tf:43-51
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
	File: test_code/modules/ec2_instance/main.tf:1-12
	Calling File: test_code/main.tf:43-51
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
	File: test_code/modules/ec2_instance/main.tf:15-40
	Calling File: test_code/main.tf:43-51
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
	File: test_code/modules/ec2_instance/main.tf:15-40
	Calling File: test_code/main.tf:43-51
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
	File: test_code/modules/ec2_instance/main.tf:1-12
	Calling File: test_code/main.tf:24-28
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
	File: test_code/modules/ec2_instance/main.tf:1-12
	Calling File: test_code/main.tf:24-28
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
	File: test_code/modules/ec2_instance/main.tf:1-12
	Calling File: test_code/main.tf:24-28
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
	File: test_code/modules/ec2_instance/main.tf:1-12
	Calling File: test_code/main.tf:24-28
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
	File: test_code/modules/ec2_instance/main.tf:15-40
	Calling File: test_code/main.tf:24-28
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
	File: test_code/modules/ec2_instance/main.tf:15-40
	Calling File: test_code/main.tf:24-28
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
	File: test_code/modules/ec2_instance/main.tf:15-40
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
	File: test_code/modules/ec2_instance/main.tf:15-40
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
	File: test_code/modules/ec2_instance/main.tf:1-12
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
	File: test_code/modules/ec2_instance/main.tf:1-12
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

REPLACED_SINGLE_WORKDIR_BLOCK_TFSEC = \
    """
Running TFSec analysis in directory: test_code/
Issues found in directory: test_code/.

Results #1-2 CRITICAL Security group rule allows egress to multiple public internet addresses. (2 similar results)
───
  test_code/modules/ec2_instance/main.tf:38
   via test_code/main.tf:43-51 (module.ec2_instance)
───
   15    resource "aws_security_group" "this" {
   ..  
   38  [     cidr_blocks = ["0.0.0.0/0"]
   ..  
   40    }
───
  Individual Causes
  - modules/ec2_instance/main.tf:43-51 (module.ec2_instance)
  - modules/ec2_instance/main.tf:24-28 (module.key_pair)
───
          ID aws-ec2-no-public-egress-sgr
      Impact Your port is egressing data to the internet
  Resolution Set a more restrictive cidr range



Result #3 HIGH Table encryption is not enabled. 
───
  test_code/modules/dynamodb/main.tf:1-16
   via test_code/main.tf:37-40 (module.dynamodb)
───
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
───
          ID aws-dynamodb-enable-at-rest-encryption
      Impact Data can be freely read if compromised
  Resolution Enable encryption at rest for DAX Cluster



Results #4-5 HIGH Instance does not require IMDS access to require a token (2 similar results)
───
  test_code/modules/ec2_instance/main.tf:1-12
   via test_code/main.tf:43-51 (module.ec2_instance)
───
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
───
  Individual Causes
  - modules/ec2_instance/main.tf:43-51 (module.ec2_instance)
  - modules/ec2_instance/main.tf:24-28 (module.key_pair)
───
          ID aws-ec2-enforce-http-token-imds
      Impact Instance metadata service can be interacted with freely
  Resolution Enable HTTP token requirement for IMDS



Results #6-7 HIGH Root block device is not encrypted. (2 similar results)
───
  test_code/modules/ec2_instance/main.tf:1-12
   via test_code/main.tf:43-51 (module.ec2_instance)
───
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
───
  Individual Causes
  - modules/ec2_instance/main.tf:43-51 (module.ec2_instance)
  - modules/ec2_instance/main.tf:24-28 (module.key_pair)
───
          ID aws-ec2-enable-at-rest-encryption
      Impact The block device could be compromised and read from
  Resolution Turn on encryption for all block devices



Result #8 MEDIUM Point-in-time recovery is not enabled. 
───
  test_code/modules/dynamodb/main.tf:1-16
   via test_code/main.tf:37-40 (module.dynamodb)
───
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
───
          ID aws-dynamodb-enable-recovery
      Impact Accidental or malicious writes and deletes can't be rolled back
  Resolution Enable point in time recovery



Result #9 LOW Table encryption does not use a customer-managed KMS key. 
───
  test_code/modules/dynamodb/main.tf:1-16
   via test_code/main.tf:37-40 (module.dynamodb)
───
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
───
          ID aws-dynamodb-table-customer-key
      Impact Using AWS managed keys does not allow for fine grained control
  Resolution Enable server side encryption with a customer managed key



Results #10-11 LOW Security group rule does not have a description. (2 similar results)
───
  test_code/modules/ec2_instance/main.tf:34-39
   via test_code/main.tf:24-28 (module.key_pair)
───
   15    resource "aws_security_group" "this" {
   ..  
   34  ┌   egress {
   35  │     from_port   = 0
   36  │     to_port     = 0
   37  │     protocol    = "-1"
   38  │     cidr_blocks = ["0.0.0.0/0"]
   39  └   }
   40    }
───
  Individual Causes
  - modules/ec2_instance/main.tf:24-28 (module.key_pair)
  - modules/ec2_instance/main.tf:43-51 (module.ec2_instance)
───
          ID aws-ec2-add-description-to-security-group-rule
      Impact Descriptions provide context for the firewall rule reasons
  Resolution Add descriptions for all security groups rules
"""

REPLACED_NO_ISSUES_DIR_TFSEC = \
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

AI_RESPONSE_WITH_CORRECTED_FILES = \
    """
The issues reported relate to the DynamoDB table resource in `test_code/modules/dynamodb/main.tf`:

1. **Table encryption is not enabled (HIGH severity)**  
   Cause: The resource does not specify `server_side_encryption` block, so encryption at rest is not enabled.  
   Solution: Add the `server_side_encryption` block to enable encryption.

2. **Point-in-time recovery is not enabled (MEDIUM severity)**  
   Cause: The resource does not have `point_in_time_recovery` block enabled.  
   Solution: Add `point_in_time_recovery` block with `enabled = true`.

3. **Table encryption does not use a customer-managed KMS key (LOW severity)**  
   Cause: By default, enabling encryption uses AWS managed keys. To use a customer-managed key, specify the KMS key ARN or ID in the `server_side_encryption` block.  
   Solution: Add a variable for the KMS key ARN and reference it in the `server_side_encryption` block.

---

### Code snippet to fix these issues:

```hcl
resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Environment = "Test"
    ManagedBy   = "Terraform"
  }
}
```

Also, add the new variable for the KMS key ARN in `variables.tf`:

```hcl
variable "kms_key_arn" {
  description = "The ARN of the customer managed KMS key to use for DynamoDB encryption"
  type        = string
}
```

---

Corrected files with these changes:

Corrected file `test_code/modules/dynamodb/main.tf`

```hcl
resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Environment = "Test"
    ManagedBy   = "Terraform"
  }
}
```

Corrected file `test_code/modules/dynamodb/variables.tf`

```hcl
variable "table_name" {
  description = "The name of the DynamoDB table for state locking"
  type        = string
}

variable "kms_key_arn" {
  description = "The ARN of the customer managed KMS key to use for DynamoDB encryption"
  type        = string
}
```

---

If you do not have a customer-managed KMS key yet, you will need to create one or pass the ARN of an existing key. If you want to keep using the AWS managed key, you can omit `kms_key_arn` and just set `enabled = true` in the `server_side_encryption` block. Let me know if you want that variant or help creating a KMS key.
""".lstrip().removesuffix("\n")

PARSED_CORRECTED_FILENAMES_AND_CONTENT = \
    {
        'test_code/modules/dynamodb/main.tf': 'resource "aws_dynamodb_table" "this" {\n  name         = '
                                              'var.table_name\n  billing_mode = "PAY_PER_REQUEST"\n  hash_key     = '
                                              '"LockID"\n\n  attribute {\n    name = "LockID"\n    type = "S"\n  '
                                              '}\n\n  server_side_encryption {\n    enabled     = true\n    '
                                              'kms_key_arn = var.kms_key_arn\n  }\n\n  point_in_time_recovery {\n    '
                                              'enabled = true\n  }\n\n  tags = {\n    Environment = "Test"\n    '
                                              'ManagedBy   = "Terraform"\n  }\n}\n',
        'test_code/modules/dynamodb/variables.tf': 'variable "table_name" {\n  description = "The name of the '
                                                   'DynamoDB table for state locking"\n  type        = '
                                                   'string\n}\n\nvariable "kms_key_arn" {\n  description = "The ARN '
                                                   'of the customer managed KMS key to use for DynamoDB encryption"\n '
                                                   ' type        = string\n}\n'}


@pytest.fixture
def log_file_text_tflint():
    return LOG_TEXT_TFLINT, 'tflint'


@pytest.fixture
def log_file_text_no_tool_name():
    return LOG_TEXT_TFLINT, 'other_tool'


@pytest.fixture
def log_file_text_checkov():
    return LOG_TEXT_CHECKOV, 'checkov'


@pytest.fixture
def log_file_text_tfsec():
    return LOG_TEXT_TFSEC, 'tfsec'


@pytest.fixture
def log_file_text_terraform():
    return LOG_TEXT_TERRAFORM, 'Terraform'


@pytest.fixture
def expected_workdir_errors_blocks_terraform():
    return EXTRACTED_BLOCKS_TERRAFORM


@pytest.fixture
def expected_workdir_errors_blocks_tflint():
    return EXTRACTED_BLOCKS_TFLINT


@pytest.fixture
def expected_workdir_errors_blocks_tfsec():
    return EXTRACTED_BLOCKS_TFSEC


@pytest.fixture
def expected_workdir_errors_blocks_checkov():
    return EXTRACTED_BLOCKS_CHECKOV


@pytest.fixture
def replaced_workdir_errors_blocks_terraform():
    return REPLACED_WORKDIR_BLOCKS_TERRAFORM


@pytest.fixture
def replaced_workdir_errors_blocks_tfsec():
    return REPLACED_WORKDIR_BLOCKS_TFSEC


@pytest.fixture
def replaced_workdir_errors_blocks_checkov():
    return REPLACED_WORKDIR_BLOCKS_CHECKOV


@pytest.fixture
def replaced_paths_one_block_checkov():
    return REPLACED_PATHS_MONO_BLOCK_CHECKOV


@pytest.fixture
def log_text_one_block_tflint():
    return LOG_TEXT_SINGLE_DIR_TFLINT


@pytest.fixture
def extracted_paths_to_tf_files_checkov():
    return ['test_code', 'test_code/modules/ec2_instance']


@pytest.fixture
def extracted_paths_to_tf_files_tflint():
    return ['test_code/modules/dynamodb', 'test_code/modules/ec2_instance']


@pytest.fixture
def replaced_paths_one_block_tfsec():
    return REPLACED_SINGLE_WORKDIR_BLOCK_TFSEC


@pytest.fixture
def extracted_paths_to_tf_files_tfsec():
    return ['test_code/modules/dynamodb', 'test_code/modules/ec2_instance']


@pytest.fixture
def cleaned_errors_blocks_tfsec():
    return CLEANED_ERRORS_BLOCKS_TFSEC


@pytest.fixture
def no_issue_dir_blocks_tfsec():
    return LOG_TEXT_NO_ISSUES_DIR_TFSEC


@pytest.fixture
def removed_no_issue_dir_blocks_tfsec():
    return REPLACED_NO_ISSUES_DIR_TFSEC


@pytest.fixture
def ai_response_with_corrected_files_hcl_blocks():
    return AI_RESPONSE_WITH_CORRECTED_FILES


@pytest.fixture
def parsed_corrected_filenames_and_content_from_hcl_blocks():
    return PARSED_CORRECTED_FILENAMES_AND_CONTENT
