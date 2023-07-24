terraform {
  required_version = ">= 0.14"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

resource "random_uuid" "lambda_src_hash" {
  keepers = {
  for filename in setunion(
    fileset("", var.requirements),
    fileset("", "${var.scraper_lambda_root}/lambda_function.py"),
    fileset("", "${var.scraper_lambda_root}/ecbe_exchange_scraper.py"),
    fileset("", "${var.api_lambda_root}/ecbe_exchange_scraper.py"),
  ) :
  filename => filemd5(filename)
  }
}

data "archive_file" "lambda_source" {
  depends_on = [null_resource.install_dependencies_scraper]
  excludes   = [
    "__pycache__",
    "venv",
  ]

  source_dir  = var.src_root
  output_path = "${var.scraper_lambda_root}/${random_uuid.lambda_src_hash.result}.zip"
  type        = "zip"
}

resource "aws_iam_policy_attachment" "lambda_logging_policy" {
  name       = "lambda_logging_policy"
  policy_arn = aws_iam_policy.lambda_cloudwatch_logs_policy.arn
  roles      = [aws_iam_role.lambda_rds_role.name]
}

resource "aws_cloudwatch_event_rule" "lambda_trigger" {
  name                = "once_a_day_trigger"
  schedule_expression = "cron(0 0 * * ? *)"
}


resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_trigger.name
  arn       = aws_lambda_function.scraper_lambda.arn
  target_id = "lambda_target"
}

#create a security group for RDS Database Instance
resource "aws_security_group" "rds_sg" {
  name = "rds_sg"
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#create a RDS Database Instance
resource "aws_db_instance" "rds_instance" {
  engine                 = var.engine
  identifier             = var.identifier
  allocated_storage      = var.storage
  engine_version         = lookup(var.engine_version, var.engine)
  instance_class         = var.instance_class
  db_name                = var.rds_name
  username               = var.rds_username
  password               = var.rds_password
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot = "true"
  publicly_accessible = "true"
}


data "archive_file" "get_currency_lambda_source" {
  depends_on = [null_resource.install_dependencies_api]
  excludes   = [
    "__pycache__",
    "venv",
  ]

  source_dir  = var.src_root
  output_path = "${var.api_lambda_root}/${random_uuid.lambda_src_hash.result}.zip"
  type        = "zip"
}

resource "aws_lambda_function" "get_currency_data" {
  function_name    = "get_currency_data"
  runtime          = "python3.8"
  handler          = "api.lambda_function.get_currency_data"
  timeout          = 300
  memory_size      = 128
  publish          = true
  filename         = data.archive_file.get_currency_lambda_source.output_path
  source_code_hash = data.archive_file.get_currency_lambda_source.output_base64sha256

  environment {
    variables = {
      RDS_HOST     = aws_db_instance.rds_instance.address
      RDS_USERNAME = var.rds_username
      RDS_PASSWORD = var.rds_password
      RDS_NAME     = var.rds_name
    }
  }

  # Add any necessary IAM roles/policies for the Lambda function
  role = aws_iam_role.lambda_rds_role.arn
}

# Create the API Gateway
resource "aws_api_gateway_rest_api" "currency_api" {
  name = "currency_api"
}

# Create a resource for the API Gateway
resource "aws_api_gateway_resource" "currency_resource" {
  rest_api_id = aws_api_gateway_rest_api.currency_api.id
  parent_id   = aws_api_gateway_rest_api.currency_api.root_resource_id
  path_part   = "currency"
}

# Create a GET method for the resource
resource "aws_api_gateway_method" "currency_method" {
  rest_api_id   = aws_api_gateway_rest_api.currency_api.id
  resource_id   = aws_api_gateway_resource.currency_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# Configure the integration with the Lambda function
resource "aws_api_gateway_integration" "currency_integration" {
  rest_api_id = aws_api_gateway_rest_api.currency_api.id
  resource_id = aws_api_gateway_resource.currency_resource.id
  http_method = aws_api_gateway_method.currency_method.http_method
  integration_http_method = "POST"
  type                     = "AWS_PROXY"
  uri                      = aws_lambda_function.get_currency_data.invoke_arn
  depends_on               = [aws_lambda_function.get_currency_data]
}

# Create a deployment for the API
resource "aws_api_gateway_deployment" "currency_deployment" {
  rest_api_id = aws_api_gateway_rest_api.currency_api.id
  stage_name  = "prod"

  depends_on = [aws_lambda_function.get_currency_data]
}



# Grant necessary permissions to allow API Gateway to invoke the Lambda function
resource "aws_lambda_permission" "currency_api_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_currency_data.function_name
  principal     = "apigateway.amazonaws.com"

  # Replace with the appropriate ARN for your API
  source_arn = aws_api_gateway_deployment.currency_deployment.execution_arn
}

# Create zip file from requirements.txt. Triggers only when the file is updated
resource "null_resource" "install_dependencies_api" {
  triggers = {
    dependencies_versions = filemd5("${var.api_lambda_root}/requirements.txt")
    lambda_function_version = filemd5("${var.api_lambda_root}/lambda_function.py")
  }

  # The command to install the dependencies to the lambda folder and create the ZIP file
  provisioner "local-exec" {
    command = "pip3 install -r ${var.api_lambda_root}/requirements.txt -t ${var.api_lambda_root} && cd ${var.api_lambda_root} && zip -r ${path.module}/api.zip * && cd ${path.module}"
  }
}

# Create zip file from requirements.txt. Triggers only when the file is updated
resource "null_resource" "install_dependencies_scraper" {
  triggers = {
    dependencies_versions = filemd5("${var.scraper_lambda_root}/requirements.txt")
    lambda_function_version = filemd5("${var.scraper_lambda_root}/lambda_function.py")
  }

  # The command to install the dependencies to the lambda folder and create the ZIP file
  provisioner "local-exec" {
    command = "pip3 install -r ${var.scraper_lambda_root}/requirements.txt -t ${var.scraper_lambda_root} && cd ${var.scraper_lambda_root} && zip -r ${path.module}/scraper.zip * && cd ${path.module}"
  }
}

resource "aws_lambda_function" "scraper_lambda" {
  function_name    = var.lambda_function_name
  runtime          = "python3.8"
  handler          = "scraper.lambda_function.fetch_currency_data"
  timeout          = 300
  memory_size      = 128
  publish          = true
  filename         = data.archive_file.lambda_source.output_path
  source_code_hash = data.archive_file.lambda_source.output_base64sha256

  environment {
    variables = {
      RDS_HOST     = aws_db_instance.rds_instance.address
      RDS_USERNAME = var.rds_username
      RDS_PASSWORD = var.rds_password
      RDS_NAME     = var.rds_name
    }
  }

  # Add any necessary IAM roles/policies for the Lambda function
  role = aws_iam_role.lambda_rds_role.arn
}

resource "aws_iam_role" "lambda_rds_role" {
  name = "lambda_rds_role"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_cloudwatch_logs_policy" {
  name   = "lambda_cloudwatch_logs_policy"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource": "arn:aws:logs:*:*:*"
      }
    ]
  })
}


resource "aws_iam_policy_attachment" "lambda_rds_policy" {
  name       = "lambda_rds_policy"
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
  roles      = [aws_iam_role.lambda_rds_role.name]
}


resource "aws_lambda_permission" "scraper_lambda_permission" {
  statement_id  = "AllowCloudWatchToInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scraper_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_trigger.arn
}

# Output the API endpoint URL
output "api_endpoint" {
  value = aws_api_gateway_deployment.currency_deployment.invoke_url
}

