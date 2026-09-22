# 1. Main VPC
resource "aws_vpc" "main" {
  cidr_block       = var.vpc_cidr_block
  instance_tenancy = "default"

  tags = {
    Name = "main-vpc"
  }
}

# 2. Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

# 3. Public Subnet
resource "aws_subnet" "public_subnets" {
  vpc_id                  = aws_vpc.main.id
  for_each                = var.public_subnets
  cidr_block              = each.value.cidr_block
  availability_zone       = each.value.availability_zone
  map_public_ip_on_launch = true
  tags = {
    Name                     = each.key
    "kubernetes.io/role/elb" = "1"
  }
}

# 4. Private Subnets
resource "aws_subnet" "private_subnets" {
  vpc_id                  = aws_vpc.main.id
  for_each                = var.private_subnets
  cidr_block              = each.value.cidr_block
  availability_zone       = each.value.availability_zone
  map_public_ip_on_launch = false
  tags = {
    Name                              = each.key
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# 5. Public Route Table
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = {
    Name = "public-route-table"
  }
}

# 6. Route Table Association
resource "aws_route_table_association" "public_associations" {
  for_each       = aws_subnet.public_subnets
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public_route_table.id
}

# 7. NAT Gateway
resource "aws_nat_gateway" "nat-gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnets["public-subnet-1a"].id
  tags = {
    Name = "nat-gateway"
  }
}

# 8. Private Route Table
resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat-gw.id
  }
  tags = {
    Name = "private-route-table"
  }
}

# 9. Associate all Private Subnets with the Private Route Table
resource "aws_route_table_association" "private" {
  for_each       = aws_subnet.private_subnets
  subnet_id      = each.value.id
  route_table_id = aws_route_table.private_route_table.id
}

# 10. Elastic IP For the Nat Gateway
resource "aws_eip" "nat_eip" {
  domain = "vpc"
  tags = {
    Name = "nat-gateway-eip"
  }
}
