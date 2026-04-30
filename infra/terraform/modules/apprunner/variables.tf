variable "service_name" {
  type = string
}

variable "image_identifier" {
  type = string
}

variable "port" {
  type    = string
  default = "8000"
}

variable "environment" {
  type = map(string)
}
