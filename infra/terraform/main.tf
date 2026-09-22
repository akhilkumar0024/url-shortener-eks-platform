module "networking" {
  source          = "./modules/networking"
  vpc_cidr_block  = var.vpc_cidr
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
}
