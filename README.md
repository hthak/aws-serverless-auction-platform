# AWS Serverless Auction Platform

A serverless auction backend built on AWS for managing users, auctions, bids, workflow orchestration, and asynchronous event processing.

The system uses AWS Lambda and API Gateway for REST endpoints, DynamoDB for persistent storage, Step Functions for bid-processing workflows, and SNS/SQS for asynchronous event handling.

## Architecture

```text
Client
  |
  v
Amazon API Gateway
  |
  +-----------------------+
  |                       |
  v                       v
AWS Lambda          AWS Step Functions
  |                       |
  v                       v
Amazon DynamoDB     Bid Validation Workflow
                            |
                            v
                        DynamoDB
                            |
                            v
                           SNS
                            |
                            v
                           SQS
                            |
                            v
                      Logger Lambda
