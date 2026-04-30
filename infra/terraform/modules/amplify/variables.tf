variable "app_name" {
  type = string
}

variable "repository" {
  type = string
}

variable "branch_name" {
  type    = string
  default = "main"
}

variable "github_token" {
  type      = string
  sensitive = true
}

variable "environment" {
  type = map(string)
}
