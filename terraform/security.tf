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
        # allowed ip for incoming traffic 
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "api" {
    name = "cb-ec2-access-security-group"
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
        # allow api to make ougoing request everywhere 
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "worker" {
    name = "cb-ec2-access-security-group"
    description = "allow inbound access from the ALB only"
    vpc_id      = aws_vpc.main.id

    ingress {
        protocol = "tcp"
        from_port = var.redis_port
        to_port = var.redis_port

        # incoming traffic must come from api security group or elasticache 
        security_groups = [aws_security_group.redis.id]
    }

    ingress {
        protocol = "tcp"
        from_port = var.worker_port
        to_port = var.worker_port

        # incoming traffic must come from api security group or elasticache 
        security_groups = [aws_security_group.api.id]
    }

    egress {
        protocol = "-1"
        from_port = 0
        to_port = 0
        # allow api to make ougoing request everywhere 
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "redis" {
  name        = "cb-redis-security-group"
  description = "allow access to Redis only from Worker"
  vpc_id      = aws_vpc.main.id

  ingress {
    protocol        = "tcp"
    from_port       = var.redis_port
    to_port         = var.redis_port
    # only allow incoming traffic from worker and api
    security_groups = [aws_security_group.worker.id, aws_security_group.api.id] 
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"] 
  }
}