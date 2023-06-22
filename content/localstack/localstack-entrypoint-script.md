Title: Entrypoint Script with Localstack and Docker-Compose
Date: 2023-01-16
Modified: 2023-06-21
Tags: docker, docker-compose, localstack, serverless, lambda, aws, python, cloud, eventbridge ,sns, s3, sqs, api, gateway, local, developer, django, python, entrypoint
Slug: entrypoint-script-with-localstack
Author: Miguel Lopez
Summary: This guide will use entrypoint scripts to create AWS Resources in Localstack. By the end of this guide, you will have an example of to create an s3 bucket in Localstack and access it from aws-cli. 

Technical Stack: AWS, Localstack, Docker, Docker-Compose

Read: 5 minutes

## Prerequisites 

- Docker, Docker-Compose
- Localstack Docker Image 
  - _This guide has been updated for Localstack releases after March 29, 2023. [Read More Here.](https://discuss.localstack.cloud/t/new-lambda-implementation-in-localstack-2-0/258)_
  - _Earlier versions of Localstack Lambda reference `/docker-entrypoint-initaws.d/` for entrypoint scripts. That entrypoint path was deprecated in [v1.1.0](https://github.com/localstack/localstack/releases/tag/v1.1.0)._

---

## Introduction

**Localstack** is a cloud service emulator that runs in a single container on your laptop or in your CI environment. [Read More Here.](https://docs.localstack.cloud/getting-started/?__hstc=108988063.4c3716ab9432d996297196d8a59201a6.1673401275754.1673401275754.1673907003067.2&__hssc=108988063.1.1673907003067&__hsfp=1395183370)

**awslocal** is a thin wrapper for AWS CLI that overrides the AWS CLI commands with `--endpoint-url localhost:4566`.

After reading this, your docker-compose will: 

- Run Localstack in Docker-Compose
- Create mocked resources in Localstack with entrypoint scripts
- How to access Localstack services at `http://localstack:4566` or using `aws-local`

---

## Entrypoint Script to Create S3 Buckets in Localstack

1.  Create and paste the following content to `start-localstack.sh`. This will be our entrypoint scipt: 
```yml
#!/bin/bash
awslocal s3 mb s3://hsl-local-terraform --region us-west-2
awslocal s3 mb s3://hsl-local-serverless --region us-west-2
awslocal s3 ls --region us-west-2
```
2. Make the script executable by running:
```
chmod +x start-localstack.sh
```

3. Pass the `start-localstack.sh` through the `volumes:` section to the  `localstack` container:
    - Pass entrypoint startup scripts through `/etc/localstack/init/ready.d/`
    - Read here for a full list of [Localstack Lifecycle Events](https://docs.localstack.cloud/references/init-hooks/)
    - Use the `docker-compose.yml` below as a reference.

4. Start the containers using `docker-compose up` and observe the S3 buckets being made:
```
relate-lambda-template-localstack-1  | make_bucket: hsl-local-serverless
relate-lambda-template-localstack-1  | {
relate-lambda-template-localstack-1  |     "EventBusArn": "arn:aws:events:us-west-2:000000000000:event-bus/platform-service-bus"
relate-lambda-template-localstack-1  | }
relate-lambda-template-localstack-1  | 2023-06-22 04:45:49 hsl-local-serverless
```

---

## Full Docker-Compose Example
```yml
version: "3.8" 
services:
  localstack:
    image: localstack/localstack
    ports:
      - "127.0.0.1:4566:4566"            # LocalStack Gateway
      - "127.0.0.1:4510-4559:4510-4559"  # external services port range
    environment:
      AWS_DEFAULT_REGION: us-west-2
      AWS_ACCESS_KEY_ID: test
      AWS_SECRET_ACCESS_KEY: test
      DEBUG: ${DEBUG:-1}
      DOCKER_HOST: unix:///var/run/docker.sock
      LS_LOG: WARN  # Localstack DEBUG Level    
    volumes:
      - "${TMPDIR:-/tmp}/localstack:/var/lib/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"
      - ./start-localstack.sh:/etc/localstack/init/ready.d/start-localstack.sh
```
_docker-compose.yml_


---

## Access Localstack S3 Buckets 

### Access From Local Machine

1. Run this **awslocal** from your local machine:
```
$ awslocal s3 ls

2023-06-21 21:45:49 hsl-local-serverless
```

### Access from Localstack Container

1. Access the `localstack` container by running:
```
$ docker-compose exec localstack /bin/bash
```

2. Use **awslocal** to access the S3 buckets:
```
$ awslocal s3 ls

2023-06-22 04:45:49 hsl-local-serverless
```

### Access From Compose Services

1. Override Boto3 Client Endpoint URL. This will point to the Localstack container:
```python
import boto3

sns_client = boto3.client('sns', endpoint_url='http://localstack:4566')
```

---

## Benefits of Localstack

- Developers can spin up a fully localized enviornment
- Less $$ spent provisioning and cleaning up AWS
- Isolated developer environments

I hope this guide helps you quickly orchestrate localstack next to your existing applications!