output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = [for subnet in aws_subnet.public_subnets : subnet.id]
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = [for subnet in aws_subnet.private_subnets : subnet.id]
}

output "nat-gw-id" {
  description = "The ID of the NAT Gateway"
  value       = aws_nat_gateway.nat-gw.id
}

output "aws_internet_gateway" {
  description = "Id of the IGW"
  value       = aws_internet_gateway.main.id
}
