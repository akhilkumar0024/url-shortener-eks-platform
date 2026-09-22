module "networking" {
  source          = "./modules/networking"
  vpc_cidr_block  = var.vpc_cidr
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
}

module "eks_cluster" {
  source              = "./modules/eks"
  private_subnet_ids  = module.networking.private_subnet_ids
  cluster_name        = var.eks_config.cluster_name
  cluster_version     = var.eks_config.cluster_version
  node_group_name     = var.eks_config.node_group_name
  node_instance_types = var.eks_config.node_instance_types
  desired_size        = var.eks_config.desired_size
  max_size            = var.eks_config.max_size
  min_size            = var.eks_config.min_size
}

