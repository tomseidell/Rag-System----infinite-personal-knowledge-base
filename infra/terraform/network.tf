data "aws_availability_zones" "available" { # returns all possible az's of provider region
}


# define ip adress range for vpc
resource "aws_vpc" "main" {
    cidr_block = "172.17.0.0/16" 
}

# define subnet ranges for public and private subnet
resource "aws_subnet" "private" {
  count = var.az_count
  vpc_id = aws_vpc.main.id
  cidr_block = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)

  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "private-${count.index}"
  }
}
resource "aws_subnet" "public" {
  count = var.az_count
  vpc_id = aws_vpc.main.id
  map_public_ip_on_launch = true
  cidr_block = cidrsubnet(aws_vpc.main.cidr_block, 8, var.az_count + count.index)

  # based on count, choose az from above 
  availability_zone = data.aws_availability_zones.available.names[count.index]

}




# internet gateway and route table for public subnet 
resource "aws_route_table" "public" { # route table for vpc
  vpc_id = aws_vpc.main.id
}
resource "aws_route_table_association" "public" { # maps routing table to specific subnet (public subnet)
  count = var.az_count # for every subnet (count = 2), create 1 route table association 
  subnet_id = aws_subnet.public[count.index].id # connect to both public subnets 
  route_table_id = aws_route_table.public.id # connect to route table
}
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}
resource "aws_route" "internet_access" { # route for public route table. 
 route_table_id = aws_route_table.public.id # create entry in public route table
 gateway_id = aws_internet_gateway.gw.id # connect to internet gateway

 # use route for request to the internet 
 destination_cidr_block = "0.0.0.0/0"
}



# Nat gateway and route table for private subnet 
resource "aws_eip" "gw" { # elastic ip => dedicated public ip for enabling nat gateway to communicate to the internet via this ip
 count = var.az_count
 domain = "vpc" # reserve ip for vpc ressource
 depends_on = [aws_internet_gateway.gw]
}
resource "aws_nat_gateway" "gw" {
 count = var.az_count # 2 az's
 subnet_id = aws_subnet.public[count.index].id # nat gateway has to be in public subnet to successfully make requests to the internet
 allocation_id = aws_eip.gw[count.index].id # connect to elastic ip's
}
resource "aws_route_table" "private" { # route table for private subnet
    vpc_id = aws_vpc.main.id
    count = var.az_count
}
resource "aws_route_table_association" "private" { # connect route table to private subnet
  count = var.az_count
  subnet_id = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
resource "aws_route" "private" {
    count = var.az_count
    route_table_id = aws_route_table.private[count.index].id # connect to route table 
    nat_gateway_id = aws_nat_gateway.gw[count.index].id # connect to nat gateway, which is sitting in public subnet 

     # use route for request to the internet from private subnet ressources
    destination_cidr_block = "0.0.0.0/0"
}