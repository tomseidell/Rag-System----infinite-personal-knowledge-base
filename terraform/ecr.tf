# aws docker image registry


# registry for api images
resource "aws_ecr_repository" "api" {
    name = "api"
    image_tag_mutability = "MUTABLE"

    image_scanning_configuration {
        scan_on_push = true
    }  
}  


# registry for worker images
resource "aws_ecr_repository" "worker" {
    name = "worker"
    image_tag_mutability = "MUTABLE"

    image_scanning_configuration {
        scan_on_push = true
    }  
}   