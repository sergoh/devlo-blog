Title: Serverless Framework: Serverless Compose Example Project
Date: 2023-06-14
Modified: 2023-06-14
Tags: serverless, lambda, aws, cloud, developer, django, python, serverless-framework, guide
Slug: sls-framework-serverless-compose-example-project
Author: Miguel Lopez
Summary: A guide to help you deploy mutiple Serverless projects at once using Serverless Compose. By the end of this guide, you will have an example of how to organize and deploy multiple Serverless projects using Serverless Compose.

Technical Stack: AWS, Lambda, Serverless Framework

Read: 10 minutes

## Pre-Requisites

To deploy the following Serverless Framework template, you will need the following:

- An AWS account.
- AWS CLI installed locally. 
- API credentials for your AWS account configured in your AWS CLI locally by running `aws configure`.
- Serverless framework installed locally via `npm -g install serverless`.
- Serverless compose installed locally via `npm -g install serverless-compose`

## Serverless Compose Example Project

Serverless Compose is a plugin for the Serverless Framework that allows you to deploy multiple Serverless projects at once. Each project is deployed as a serperate **CloudFormation** stack in AWS with its own resources, outputs, and deployment.

Check out the following `serverless-compose.yml`:
```yml
services:
  derezzed-base-infrastructure:
    path: infrastructure/derezzed-base-infrastructure/
  derezzed-db-infrastructure:
    path: infrastructure/derezzed-db-infrastructure/
  derezzed-fastapi-lambda:
    path: lambdas/derezzed-fastapi-lambda/
    dependsOn:
      - derezzed-base-infrastructure
    params:
      derezzedSQSArn: ${derezzed-base-infrastructure.derezzedSQSArn}
```

`services:` - You organize your servless projects into seperate *services*. Each of these `services:` will create a seperate **CloudFormation** stack in AWS.

`path:` - Relative path to the **serverless.yml** file for your Serverless Framework project.

`depdendsOn:` - Create dependencies between your Serverless projects. In this example, the **derezzed-fastapi-lambda** service depends on the **derezzed-base-infrastructure** service. This means the **derezzed-base-infrastructure** service will be deployed first. 

`params:` - Pass outputs from one service to another. In this example, the **derezzed-base-infrastructure** service is passing the **sqsRelateAsyncArn** output to the **derezzed-fastapi-lambda** service.

## Deploying with Serverless Compose

You will run the normal `sls` commands to run serverless compose. 

```bash
sls deploy --stage dev
```

You can also deploy individual services by running the following command:

```bash
sls deploy --stage dev --service derezzed-fastapi-lambda
```

Your output will look similar to this:
```bash
sls deploy --stage dev
Running "serverless" from node_modules

Deploying to stage dev

    ✔  derezzed-base-infrastructure › deployed › 9s
    ✔  derezzed-requirements-layer › deployed › 10s
    ✔  derezzed-fastapi-lambda › deployed › 50s
```

## Improving Serverless Application Resiliency

Use Serverless Compose to improve the resiliency of your application. Think about splitting important resources like **databases, queues, and layers** into their own Serverless projects. This allows you to preserve those key resources should you need to delete and redeploy your Lambda functions completely.

You don't want to be the person who accidentally deletes the production database because you were trying to fix a bug in your Lambda function.

Seperate your concerns and use Serverless Compose to deploy them all at once.