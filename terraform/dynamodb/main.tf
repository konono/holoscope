provider "aws" {
  profile = "holoscope"
  region  = "ap-northeast-1"
}
 
resource "aws_dynamodb_table" "holoscope" {
  name           = "holoscope"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "hashKey"
 
  attribute {
    name = "hashKey"
    type = "S"
  }
}
