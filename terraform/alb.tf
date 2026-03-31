resource "aws_alb" "main" {
    name = "cb-load-balancer"
    # all public subnets (all az's)
    subnets = aws_subnet.public.*.id
    security_groups = [aws_security_group.lb.id]
}

resource "aws_alb_target_group" "api" {
    name = "cb-target-group"

    # connected service must listen on port 8000
    port = 8000

    # communication between load balancer and service
    protocol = "HTTP"
    vpc_id = aws_vpc.main.id
    target_type = "ip"

    health_check {
        healthy_threshold = "3"
        interval = "30"
        protocol = "HTTP"
        matcher = "200"
        timeout = "3"
        path = var.health_check_path
        unhealthy_threshold = "2"
    }
}

# listener receives incoming internet traffic 
resource "aws_alb_listener" "main" {
  # connect to load balancer
  load_balancer_arn = aws_alb.main.id
  # port for incoming requests
  port = var.api_port
  protocol = "HTTP"

  default_action {
    # move traffic forward to alb target group
    target_group_arn = aws_alb_target_group.api.id
    type = "forward"
  }
}