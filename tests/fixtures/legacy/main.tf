resource "aws_instance" "web" {
  ami           = "ami-12345"
  instance_type = "t3.micro"
}

module "network" {
  source = "./modules/network"
}

variable "region" {
  default = "us-east-1"
}

output "ip" {
  value = aws_instance.web.public_ip
}
