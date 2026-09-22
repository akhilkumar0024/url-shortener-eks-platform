output "vpc_id" {
  description = "ID Of the VPC"
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.networking.private_subnet_ids
}

output "nat-gw-id" {
  description = "ID of the NAT Gateway"
  value       = module.networking.nat-gw-id
}

output "aws_internet_gateway" {
  description = "ID of the IGW"
  value       = module.networking.aws_internet_gateway
}
