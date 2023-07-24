# Currency Exchange Tracking Application

This repository contains the code and resources for a currency exchange tracking application in the AWS Lambda environment. The application fetches exchange rates from the European Central Bank Data (https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html) on a daily basis and stores them in a database.

## Technical Details

### Technologies Used
- Python
- AWS Lambda
- AWS CloudWatch
- AWS API Gateway
- AWS DynamoDB
- Terraform

### Folder Structure
- `main.tf`: Terraform configuration file containing all the AWS resources including scraper lambda, API lambda function, API Gateway, and RDS database.
- `src/scraper/lambda_function.py`: Python script for the scraper lambda function, which fetches data from the website and puts it into the database using a CloudWatch event triggered daily.
- `src/api/lambda_function.py`: Python script for the API lambda function, which fetches data from RDS and returns it in JSON format.
- `README.md`: This file, providing an overview of the application and instructions to run it.

## How to Run the Application

1. Make sure you have the necessary AWS credentials set up to deploy and execute the Lambda functions and other resources.

2. Deploy the AWS resources using Terraform (or your preferred IaC framework). Use `main.tf` to create the Lambda functions, API Gateway, RDS database, and other required resources.

3. Once the resources are deployed, the scraper lambda will start fetching exchange rates from the European Central Bank Data every day and store them in the RDS database.

4. Access the API endpoint provided by the API Gateway to view the current exchange rate information and their changes compared to the previous day.

5. Enjoy tracking the currency exchange rates with ease!

## Instructions to Run Tests Using pytest

To run the tests for this currency exchange tracking application locally, follow these steps:

1. Ensure you have Python and pytest installed on your local machine.

2. Navigate to the root directory of the project (where `src` and other files are located).

3. Open a terminal or command prompt in this directory.

4. Run the following command to execute the tests using pytest:
```bash
pytest
