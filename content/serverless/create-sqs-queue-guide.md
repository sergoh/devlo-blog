Title: Serverless Framework Guide: Create an SQS Queue
Date: 2023-06-10
Modified: 2023-06-10
Tags: serverless, lambda, aws, python, cloud, developer, django, python, rds, serverless-framework, guide, python3.9, postgres, mysql, aurora, sqs, simple, queue, service, serverless-sqs, serverless-sqs-queue
Slug: sls-framework-guide-creating-serverless-rds-cluster
Author: Miguel Lopez
Summary: A guide to help you deploy an SQS queue using the Serverless Framework. By the end of this guide, you will have an SQS queue deployed by Serverless Framework and connected to your Lambda Functions.

Technical Stack: AWS, Lambda, Serverless Framework, SQS Queue

Read: 10 minutes

## Pre-Requisites

To deploy the following Serverless Framework template, you will need the following:

- An AWS account.
- AWS CLI installed locally. 
- API credentials for your AWS account configured in your AWS CLI locally by running `aws configure`.
- Serverless framework installed locally via `npm -g install serverless`.


## Creating an SQS Queue

Using Serverless Framwework, the following `serverless.yml` example creates these resources in AWS:
- [AWS::SQS::Queue](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html)

```yml
service: derezzed-base-infrastructure
frameworkVersion: '3'

provider:
  name: aws
  stage: ${opt:stage, 'dev'}
  runtime: 'python3.9'
  region: 'us-west-2'
  deploymentBucket:
    name: serverless-deployments
    serverSideEncryption: AES256
  tags:
    stage: ${opt:stage, 'dev'}

resources:
  Resources:
    DerezzedMessagesQueue:
      Type: "AWS::SQS::Queue"
      Properties:
        QueueName: hsl-${opt:stage, self:provider.stage}-derezzed-messages
        DelaySeconds: 0
        MessageRetentionPeriod: 345600 # 4 days
        VisibilityTimeout: 30

  Outputs:
    sqsArn:
      Value: !GetAtt DerezzedMessagesQueue.Arn
    sqsUrl:
      Value: !GetAtt DerezzedMessagesQueue.QueueUrl
```

## Deploying the Serverless RDS Cluster

Run the following command to deploy the Serverless RDS Cluster:

```bash
sls deploy --stage dev
```

You'll see the following output when creating this cluster. A fresh database deployment can take up to ~5 minutes.

```bash
Running "serverless" from node_modules

Deploying to stage dev

    ✔  derezzed-base-infrastructure › deployed › 10s
```

Run `sls outputs --stage dev` to see the outputs of the deployment. You'll see the following:

```bash
Running "serverless" from node_modules

derezzed-base-infrastructure:
  sqsUrl: https://sqs.us-west-2.amazonaws.com/xxxxxxx/hsl-dev-derezzed-messages
  sqsArn: arn:aws:sqs:us-west-2:xxxxxx:hsl-dev-derezzed-messages
```

## Connecting to SQS from your Lambda

IAM access to SQS is automatically granted to your Lambda Function with the `events` block. You can use the following serverless.yml to grant your lamdba function access to SQS:

```yml
functions:
  sample:
    handler: handler.example
    events:
      - sqs:
          arn: !GetAtt DerezzedMessagesQueue.Arn
```

For a full list of SQS attributes you can use in your serverless.yml, [read the Serverless Framework SQS Docs](https://www.serverless.com/framework/docs/providers/aws/events/sqs/).