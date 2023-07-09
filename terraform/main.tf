terraform {
  required_version = ">= 0.14"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

resource "aws_lambda_function" "scraper_lambda" {
  function_name    = var.lambda_function_name
  runtime          = "python3.8"
  handler          = "lambda.handler"
  timeout          = 300
  memory_size      = 128

  # Path to the directory containing your scraping script code
  filename         = "../src/scraper/lambda_function.py"

  environment {
    variables = {
      RDS_HOST     = aws_db_instance.rds_instance.address
      RDS_USERNAME = var.rds_username
      RDS_PASSWORD = var.rds_password
    }
  }

  # Add any necessary IAM roles/policies for the Lambda function
  role = aws_iam_role.scraper_lambda_role.arn
}

resource "aws_iam_role" "scraper_lambda_role" {
  name = "scraper_lambda_role"

  assume_role_policy = <<EOF
{
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
}
EOF
}

resource "aws_iam_policy_attachment" "rds_full_access_attachment" {
  name       = "rds_full_access_attachment"
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
  roles      = [aws_iam_role.scraper_lambda_role.name]
}

resource "aws_iam_policy_attachment" "cloudwatch_events_full_access_attachment" {
  name       = "cloudwatch_events_full_access_attachment"
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchEventsFullAccess"
  roles      = [aws_iam_role.scraper_lambda_role.name]
}

resource "aws_lambda_permission" "scraper_lambda_permission" {
  statement_id  = "AllowCloudWatchToInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scraper_lambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_trigger.arn
}

resource "aws_cloudwatch_event_rule" "lambda_trigger" {
  name                = "daily_lambda_trigger"
  schedule_expression = "cron(0 0 * * ? *)"  # Trigger once a day at midnight

  # Specify any additional rule configuration if required
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_trigger.name
  arn       = aws_lambda_function.scraper_lambda.arn
  target_id = "lambda_target"
}

resource "aws_db_instance" "rds_instance" {
  engine               = "mysql"
  instance_class       = "db.t2.micro"
  allocated_storage    = 10
  storage_type         = "gp2"
  username             = var.rds_username
  password             = var.rds_password

  # Specify any additional RDS configuration if required
}
