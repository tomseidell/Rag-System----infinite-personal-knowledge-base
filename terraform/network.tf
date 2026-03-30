data "aws_availability_zones" "available" {
}

# define ip adress range
resource "aws_vpc" "main" {
    cidr_block = "172.17.0.0/16" 
}

# define subnet ranges
resource "aws_subnet" "private" {
  count = var.az_count
  vpc_id = aws_vpc.main.id
  cidr_block = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
}
resource "aws_subnet" "public" {
  count = var.az_count
  vpc_id = aws_vpc.main.id
  map_public_ip_on_launch = true
  cidr_block = cidrsubnet(aws_vpc.main.cidr_block, 8, var.az_count + count.index)
}




# internet gateway and route table for public subnet 
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
}
resource "aws_route_table_association" "public" {
  count = var.az_count
  subnet_id = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}
resource "aws_route" "internet_access" {
 route_table_id = aws_route_table.public.id
 gateway_id = aws_internet_gateway.gw.id

 # use route for request to the internet 
 destination_cidr_block = "0.0.0.0/0"
}

# Nat gateway and route table for private subnet 
resource "aws_eip" "gw" {
 count = var.az_count
 domain = "vpc"
 depends_on = [aws_internet_gateway.gw]
}
resource "aws_nat_gateway" "gw" {
 count = var.az_count
 subnet_id = aws_subnet.public[count.index].id
 allocation_id = aws_eip.gw[count.index].id
}
resource "aws_route_table" "private" {
    vpc_id = aws_vpc.main.id
    count = var.az_count
}
resource "aws_route_table_association" "private" {
  count = var.az_count
  subnet_id = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
resource "aws_route" "private" {
    count = var.az_count
    route_table_id = aws_route_table.private[count.index].id
    nat_gateway_id = aws_nat_gateway.gw[count.index].id

     # use route for request to the internet 
    destination_cidr_block = "0.0.0.0/0"
}