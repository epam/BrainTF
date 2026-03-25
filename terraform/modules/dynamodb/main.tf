# ======================= Create a DynamoDB table =======================
module "dynamodb_table" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table.git?ref=495d7a5e6ee9a45ae985a4160d9242c8b8727d69"

  name                               = var.name
  hash_key                           = var.hash_key
  range_key                          = var.range_key
  attributes                         = var.attributes
  billing_mode                       = var.billing_mode
  server_side_encryption_enabled     = var.server_side_encryption_enabled
  server_side_encryption_kms_key_arn = var.server_side_encryption_kms_key_arn
  point_in_time_recovery_enabled     = var.point_in_time_recovery_enabled
  ttl_attribute_name                 = var.ttl_attribute_name
  ttl_enabled                        = var.ttl_enabled
  tags                               = var.tags
}
