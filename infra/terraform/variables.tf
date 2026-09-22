variable "region" {
  description = "AWS Region to deploy resources in"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment (dev, testing, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project used for resource naming and tagging"
  type        = string
  default     = "url-shortener"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}


variable "public_subnets" {
  description = "Private Subnets with CIDRs and AZs"
  type = map(object({
    cidr_block        = string,
    availability_zone = string
  }))
  default = {
    "public-subnet-1a" = {
      cidr_block        = "10.0.1.0/24",
      availability_zone = "ap-south-1a"
    },
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
    },
    "private-subnet-1b" = {
      cidr_block        = "10.0.4.0/24",
      availability_zone = "ap-south-1b"
    }
  }
}

variable "eks_config" {
  description = "EKS Cluster and Node Group configuration"
  type = object({
    cluster_name        = optional(string, "url_shortener_cluster")
    cluster_version     = optional(string, "1.35")
    node_group_name     = optional(string, "eks_url_shortener_ng")
    node_instance_types = optional(list(string), ["t3.medium"])
    desired_size        = optional(number, 2)
    min_size            = optional(number, 1)
    max_size            = optional(number, 3)
  })
  default = {}
}

