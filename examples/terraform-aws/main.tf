terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "network" {
  source     = "./modules/network"
  cidr_block = var.vpc_cidr
  env        = var.environment
}

resource "aws_security_group" "web" {
  name   = "web-sg"
  vpc_id = module.network.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "web" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = module.network.public_subnet_id
  vpc_security_group_ids = [aws_security_group.web.id]

  tags = {
    Name        = "web-${var.environment}"
    Environment = var.environment
  }
}
