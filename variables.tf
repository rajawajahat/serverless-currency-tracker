variable "lambda_function_name" {
  type    = string
  default = "fetch_currency_data"
}

variable "aws_region" {
    default = "us-east-1"
    description = "AWS Region to deploy to"
}


variable "vpc_cidr" {
default = "10.0.0.0/16"
}

variable "identifier" {
  default     = "mydb-rds"
  description = "Identifier for your DB"
}

variable "storage" {
  default     = "10"
  description = "Storage size in GB"
}

variable "engine" {
  default     = "mysql"
  description = "Engine type, here it is mysql"
}

variable "engine_version" {
  description = "Engine version"

  default = {
    mysql    = "8.0.28"
  }
}

variable "instance_class" {
  default     = "db.t2.micro"
  description = "Instance class"
}

variable "rds_name" {
  default     = "mydb"
  description = "db name"
}

variable "rds_username" {
  default     = "username"
  description = "User name"
}

variable "rds_password" {
  description = "RDS root user password"
  default = ""
  sensitive   = true
}
variable "subnet_1_cidr" {
  default     = "10.0.2.0/24"
  description = "Your AZ"
}

variable "subnet_2_cidr" {
  default     = "10.0.3.0/24"
  description = "Your AZ"
}

variable "az_1" {
  default     = "us-east-1a"
  description = "Your Az1, use AWS CLI to find your account specific"
}

variable "az_2" {
  default     = "us-east-1b"
  description = "Your Az2, use AWS CLI to find your account specific"
}

variable "src_root" {
  default     = "./src"
  description = "Path to the api lambda root."
}

variable "scraper_lambda_root" {
  default     = "./src/scraper"
  description = "Path to the scraper lambda root."
}

variable "api_lambda_root" {
  default     = "./src/api"
  description = "Path to the api lambda root."
}

variable "requirements" {
  default     = "./requirements.txt"
  description = "Relative path to the requirements.txt."
}

variable "requirements_zip" {
  default     = "requirements.zip"
  description = "Path to the requirements zip file."
}