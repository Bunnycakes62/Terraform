variable "aws_region" {
        default  = "us-west-2"
}

variable "vpc_cidr" {
        default = "10.0.0.0/16"
}

variable "subnets_cidr" {
        type = list(string)
        default = ["10.0.1.0/24","10.0.2.0/24"]
}

variable "aws_az" {
        type = list(string)
        default = ["us-west-2b", "us-west-2a"]
}
