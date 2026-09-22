region       = "ap-south-1"
environment  = "dev"
project_name = "url-shortener"
vpc_cidr     = "10.0.0.0/16"
private_subnets = {
  "private-subnet-1a" = {
    cidr_block        = "10.0.3.0/24",
    availability_zone = "ap-south-1a"
  },
  "private-subnet-1b" = {
    cidr_block        = "10.0.4.0/24",
    availability_zone = "ap-south-1b"
  }
}
public_subnets = {
  "public-subnet-1a" = {
    cidr_block        = "10.0.1.0/24",
    availability_zone = "ap-south-1a"
  },
  "public-subnet-1b" = {
    cidr_block        = "10.0.2.0/24",
    availability_zone = "ap-south-1b"
  }
}

eks_config = {
  cluster_name        = "url_shortener_cluster"
  cluster_version     = "1.35"
  node_group_name     = "eks_url_shortener_ng"
  node_instance_types = ["t3.medium"]
  desired_size        = 2
  min_size            = 1
  max_size            = 3
}

