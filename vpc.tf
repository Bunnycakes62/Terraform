
# VPC
 resource "aws_vpc" "vpc-ces592-a9" {
        cidr_block       = var.vpc_cidr
        instance_tenancy = "default"
        enable_dns_support = true
        enable_dns_hostnames = true

        tags = {
                Name = "vpc-ces592-a9"
                Assignment = "9"
                Subsection = "4"
        }
}

# Two Subnets
resource "aws_subnet" "subnet-ces592-a9" {
        count = length(var.subnets_cidr)
        vpc_id = aws_vpc.vpc-ces592-a9.id
        cidr_block = element(var.subnets_cidr,count.index)
        availability_zone = element(var.aws_az, count.index)

        tags = {
                Name =" sn-ces592-a9-${count.index+1}"
                Assignnment = "9"
                Subsection = "4"
        }
}

# Two more subnets, public, made during leccture 13
resource "aws_subnet" "pri_a" {
        vpc_id = aws_vpc.vpc-ces592-a9.id
        cidr_block = "10.0.3.0/24"
        availability_zone = "us-west-2a"

        tags = {
                Name = "pri_a"
                Assignment =  "Lecture 13"
        }
}

resource "aws_subnet" "pri_b" {
        vpc_id = aws_vpc.vpc-ces592-a9.id
        cidr_block = "10.0.4.0/24"
        availability_zone = "us-west-2b"
        tags = {
                Name = "pri_b"
                Assignment = "Lecture 13"
        }
}


# NAT gateway made during lecture 13
resource "aws_nat_gateway" "nat_gw_a" {
        allocation_id = aws_eip.nat_gw_a.id
        subnet_id = aws_subnet.subnet-ces592-a9[0].id

        tags = {
                Name = "Nat Gw A"
        }
}

resource "aws_nat_gateway" "nat_gw_b" {
        allocation_id = aws_eip.nat_gw_b.id
        subnet_id = aws_subnet.subnet-ces592-a9[1].id

        tags = {
                Name = "Nat Gw B"
        }
}


# IGW
resource "aws_internet_gateway" "igw-ces592-a9" {
        vpc_id = aws_vpc.vpc-ces592-a9.id

        tags = {
                Name = "igw-ces592-a9"
                Assignemnt = "9"
                Subsection = "4"
        }
}


# Route Table
resource "aws_route_table" "rt-ces592-a9" {
        vpc_id = aws_vpc.vpc-ces592-a9.id
        route {
                cidr_block = "0.0.0.0/0"
                gateway_id = aws_internet_gateway.igw-ces592-a9.id
        }
}

resource "aws_route_table_association" "subnet-ces592-a9" {
        for_each = toset([for subnet in aws_subnet.subnet-ces592-a9: subnet.id])
        subnet_id = each.value
        route_table_id = aws_route_table.rt-ces592-a9.id
}

# Route Table for Lecture 13
resource "aws_route_table" "route_table_pri_a" {
        vpc_id = aws_vpc.vpc-ces592-a9.id
        route {
                cidr_block = "0.0.0.0/0"
                nat_gateway_id = aws_nat_gateway.nat_gw_a.id
        }
}

resource "aws_route_table" "route_table_pri_b" {
        vpc_id = aws_vpc.vpc-ces592-a9.id
        route {
                cidr_block = "0.0.0.0/0"
                nat_gateway_id = aws_nat_gateway.nat_gw_b.id
        }
}esource "aws_route_table_association" "pri_a" {
        subnet_id = aws_subnet.pri_a.id
        route_table_id = aws_route_table.route_table_pri_a.id
}

resource "aws_route_table_association" "pri_b" {
        subnet_id = aws_subnet.pri_b.id
        route_table_id = aws_route_table.route_table_pri_b.id
}


# Make a subnet group
resource "aws_db_subnet_group" "subg-ces592-a10"{
        name = "subg-ces592-a10"
        subnet_ids = [aws_subnet.subnet-ces592-a9[0].id,aws_subnet.subnet-ces592-a9[1].id]

        tags = {
                Name = "subg-ces592-a10"
                Assignment = "10"
                Subsection = "5"
        }
}

# Lecture 13 EIP
resource "aws_eip" "nat_gw_a" {
        vpc = true
}

resource "aws_eip" "nat_gw_b" {
        vpc = true
}
