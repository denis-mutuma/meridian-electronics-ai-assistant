variable "name_prefix" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "ecs_sg_id" {
  type = string
}

variable "health_check_path" {
  type    = string
  default = "/health"
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "alb_sg_name" {
  type    = string
  default = ""
}

variable "alb_sg_description" {
  type    = string
  default = "Managed by Terraform"
}