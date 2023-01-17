Title: Entrypoint Script with Localstack and Docker-Compose
Date: 2022-01-16
Modified: 2022-01-16
Tags: docker, docker-compose, localstack, serverless, lambda, aws, python, cloud, eventbridge ,sns, s3, sqs, api, gateway, local, developer, django, python, entrypoint
Slug: entrypoint-script-with-localstack
Author: Miguel Lopez
Summary: Use Entrypoint Script to Automatically Provision AWS Resources in Localstack

Technical Stack: AWS, Localstack, Docker, Docker-Compose

Read: 2 minutes

## Prerequisites 

- Docker, Docker-Compose
- Localstack Docker Image

## Introduction

**Localstack** is a cloud service emulator that runs in a single container on your laptop or in your CI environment. [Read More Here.](https://docs.localstack.cloud/getting-started/?__hstc=108988063.4c3716ab9432d996297196d8a59201a6.1673401275754.1673401275754.1673907003067.2&__hssc=108988063.1.1673907003067&__hsfp=1395183370)

After reading this, your docker-compose will: 

- Run Localstack
- Create mocked resources in Localstack upon launch
- Local AWS services can be mocked at `http://localstack:4566`


## Entrypoint Script to Create Mock S3 Buckets in Localstack

- Create and paste the following content to `start-localstack.sh`. This will be our entrypoint scipt. 
    - `awslocal` is a thin wrapper for AWS CLI that overriddes the AWS `endpoint-url` to `localhost:4566`.
    - When using the default `aws` CLI be sure to set the flag `--endpoint-url` to `localhost:4566` manually. 
```yml
awslocal s3 mb s3://hsl-local-terraform --region us-west-2
awslocal s3 mb s3://hsl-local-serverless --region us-west-2
awslocal s3 ls --region us-west-2
```
- Pass the `start-localstack.sh` script in through our `localstack` container in the `volume` section. 
    - All localstack entrypoint files are located at `/docker-entrypoint-initaws.d/`
```yml
version: "3.8" 
services:
    localstack:
        image: localstack/localstack
        ...
        volumes:
            - "${TMPDIR:-/tmp}/localstack:/var/lib/localstack"
            - "/var/run/docker.sock:/var/run/docker.sock"
            - ./start-localstack.sh:/docker-entrypoint-initaws.d/start-localstack.sh
```
- Start the containers using `docker-compose up` and observe the S3 buckets being made. 
```
localstack-1  | /usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initaws.d/start-localstack.sh
localstack-1  | make_bucket: hsl-local-terraform
localstack-1  | make_bucket: hsl-local-serverless
localstack-1  | 2023-01-16 23:43:34 hsl-local-terraform
localstack-1  | 2023-01-16 23:43:34 hsl-local-serverless
```

## Access the S3 Buckets Across Docker Compose Containers

If you're running additional containers alongside the `localstack` container, you will need to access the `localstack` container using the URL `http://localstack:4566`. Any boto3 S3 client will need `endpoint_url` overridden for `localstack`.

If you're running commands inside the `localstack` container, then you can stick to `localhost:4566` since you're not on the local network. 

## Full Docker-Compose Example
```yml
version: "3.8" 
services:
    localstack:
        image: localstack/localstack
        ports:
            - 4566:4566            # LocalStack Edge Proxy
        environment:
        AWS_DEFAULT_REGION: us-west-2
        AWS_ACCESS_KEY_ID: test
        AWS_SECRET_ACCESS_KEY: test
        DEBUG: ${DEBUG:-1}
        DEFAULT_REGION: us-west-2
        DOCKER_HOST: unix:///var/run/docker.sock
        DATA_DIR: ${DATA_DIR-}
        LAMBDA_EXECUTOR: ${LAMBDA_EXECUTOR:-local}
        LS_LOG: WARN
        HOST_TMP_FOLDER: ${TMPDIR:-/tmp/}localstack
        HOSTNAME: localstack
        HOSTNAME_EXTERNAL: localstack
        USE_SINGLE_REGION: 1
        volumes:
            - "${TMPDIR:-/tmp}/localstack:/var/lib/localstack"
            - "/var/run/docker.sock:/var/run/docker.sock"
            - ./start-localstack.sh:/docker-entrypoint-initaws.d/start-localstack.sh
```

## Overall Benefits of Localstack

- Developers can spin up a fully localized enviornment
- Less $$ spent provisioning and cleaning up AWS
- Isolated developer environments

I hope this guide helps you quickly orchestrate localstack next to your existing applications!

- Miguel Lopez