resource "aws_db_subnet_group" "main" {
    name       = "main-db-subnet-group"
    subnet_ids = aws_subnet.private.*.id 
}

resource "aws_db_instance" "postgres" {
    identifier        = "main-postgres"
    engine            = "postgres"
    # latest supported pg version
    engine_version    = "18.1"

    # smallest instance
    instance_class    = "db.t3.micro"  
    
    # min amount of storage (gb)
    allocated_storage = 20  

    db_name = var.db_name
    username = var.db_user

    backup_retention_period = 3 # 3 days backup

    # secret manager creates db password at runtime
    # automatically rotates password every 7 days 
    manage_master_user_password = true

    
    db_subnet_group_name   = aws_db_subnet_group.main.name
    vpc_security_group_ids = [aws_security_group.rds.id]
    
    # encrypt disk
    storage_encrypted = true

    multi_az            = false  
    skip_final_snapshot = true 

}
