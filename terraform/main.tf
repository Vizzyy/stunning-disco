terraform {
  required_version = ">=1.0.0"

  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }

  backend "s3" {
    bucket = "vizzyy-terraform"
    key    = "stunning-disqo/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}
