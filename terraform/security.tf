# which ip adresses can call certain services
# which ip adresses can a certain service call


resource "aws_security_group" "load_balancer" {
    name        = "cb-load-balancer-security-group"
    description = "controls access to the ALB"
    vpc_id      = aws_vpc.main.id

    # incoming Traffic
    ingress {
        # only layer 4 connections
        protocol    = "tcp"

        # allow incoming and outgoing traffic on this port range (from - to)
        from_port   = var.api_port
        to_port     = var.api_port
        # allowed ip
        cidr_blocks = ["0.0.0.0/0"] 
    }

    # outgoing Traffic
    egress {
        # allow all protocols
        protocol    = "-1"

        # allow all ports for outgoing traffic
        from_port   = 0
        to_port     = 0
        # allowed ip for outgoing traffic 
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "api" {
    name = "cb-api-security-group"
    description = "allow inbound access from the ALB only"
    vpc_id      = aws_vpc.main.id

    ingress {
        protocol = "tcp"
        from_port = var.api_port
        to_port = var.api_port

        # incoming traffic must come from load_balancer security group
        security_groups = [aws_security_group.load_balancer.id]
    }

    egress {
        protocol = "-1"
        from_port = 0
        to_port = 0
        # allow api to make outgoing request everywhere 
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "worker" {
    name = "cb-worker-security-group"
    description = "allow inbound access from api"
    vpc_id      = aws_vpc.main.id

    ingress {
        protocol = "tcp"
        from_port = var.worker_port
        to_port = var.worker_port

        # incoming traffic must come from api security group
        security_groups = [aws_security_group.api.id]
    }

    egress {
        protocol = "-1"
        from_port = 0
        to_port = 0
        # allow worker to make outgoing request everywhere 
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# Redis SG without inline rules to avoid cycle with worker SG
resource "aws_security_group" "redis" {
    name        = "cb-redis-security-group"
    description = "allow access to Redis from API and Worker"
    vpc_id      = aws_vpc.main.id
}

# only allow incoming traffic from api
resource "aws_security_group_rule" "redis_from_api" {
    type                     = "ingress"
    from_port                = var.redis_port
    to_port                  = var.redis_port
    protocol                 = "tcp"
    security_group_id        = aws_security_group.redis.id
    source_security_group_id = aws_security_group.api.id
}

# only allow incoming traffic from worker
resource "aws_security_group_rule" "redis_from_worker" {
    type                     = "ingress"
    from_port                = var.redis_port
    to_port                  = var.redis_port
    protocol                 = "tcp"
    security_group_id        = aws_security_group.redis.id
    source_security_group_id = aws_security_group.worker.id
}

resource "aws_security_group" "rds" {
    name   = "rds-security-group"
    vpc_id = aws_vpc.main.id

    # allow api and worker to call db
    ingress {
        protocol        = "tcp"
        from_port       = 5432
        to_port         = 5432
        security_groups = [aws_security_group.api.id, aws_security_group.worker.id]
    }
}
