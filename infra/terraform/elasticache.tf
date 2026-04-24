resource "aws_elasticache_subnet_group" "main" {
  name       = "main-redis-subnet-group"
  subnet_ids = aws_subnet.private.*.id
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "main-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  port                 = var.redis_port
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
}
