variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "Public Subnets with CIDRs and AZs"
  type = map(object({
    cidr_block        = string,
    availability_zone = string
  }))
  default = {
    "public-subnet-1a" = {
      cidr_block        = "10.0.1.0/24",
      availability_zone = "ap-south-1a"
    }
    "public-subnet-1b" = {
      cidr_block        = "10.0.2.0/24",
      availability_zone = "ap-south-1b"
    }
  }
}


variable "private_subnets" {
  description = "Private Subnets with CIDRs and AZs"
  type = map(object({
    cidr_block        = string,
    availability_zone = string
  }))
  default = {
    "private-subnet-1a" = {
      cidr_block        = "10.0.3.0/24",
      availability_zone = "ap-south-1a"
    }
    "private-subnet-1b" = {
      cidr_block        = "10.0.4.0/24",
      availability_zone = "ap-south-1b"
    }
  }
}
