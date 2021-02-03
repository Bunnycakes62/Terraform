terraform {
        required_version = ">= 0.13.5"
        }

provider "aws" {
        region = var.aws_region
        version = "3.12.0"
        profile = "default" # From a ~/.aws/credentials file.
        }

