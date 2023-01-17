Title: Run Localstack with Docker-Compose
Date: 2022-01-16
Modified: 2022-01-16
Tags: docker, docker-compose, localstack, serverless, lambda, aws, python, cloud, eventbridge ,sns, s3, sqs, api, gateway, local, developer, django, python
Slug: run-localstack-with-docker-compose
Author: Miguel Lopez
Summary: Use Localstack to Mock AWS Services For Local Containers

Technical Stack: AWS, Localstack, Docker, Docker-Compose

Read: 5 minutes

## Prerequisites 

- Docker, Docker-Compose
- Localstack Docker Image

## Introduction

Looking to run AWS services locally and improve the development experience? Are you hoping to make a fully isolated enviornment with no (real) shared AWS resources? Then look no further!

**Localstack** is a cloud service emulator that runs in a single container on your laptop or in your CI environment. [Read More Here.](https://docs.localstack.cloud/getting-started/?__hstc=108988063.4c3716ab9432d996297196d8a59201a6.1673401275754.1673401275754.1673907003067.2&__hssc=108988063.1.1673907003067&__hsfp=1395183370)

After reading this, your application will: 

- Run Localstack in docker-compose
- Local AWS services can be mocked at `http://localstack:4566`
- Boto3 Client is overridden to point to Localstack in docker-compose


## Localstack on Docker Compose

In this example, I will start two services through docker-compose, `localstack` and `api`: 

- `localstack` runs the AWS Emulator and will expose AWS services at `http://localstack:4566`. 
- `api` is running a Django API Server

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
    api:
        build:
            dockerfile: Dockerfile
        environment:
            AWS_ENDPOINT_URL: http://localstack:4566
            CELERY_BROKER_URL: sqs://test:test@localstack:4566
            DJANGO_SETTINGS_MODULE: messages.settings.docker_localstack
            LOG_HANDLER: console
            LOG_LEVEL: "INFO"
            PYTHONUNBUFFERED: 1
        depends_on:
            - localstack
        ports:
            - "80:80"
        command: uwsgi --http 0.0.0.0:9090 --wsgi-file messages/wsgi/dev.py --callable application --uid appuser --gid appuser --enable-threads
```
1. Copy and paste the following code into `docker-compose.yml`.

2. Build the images: `docker-compose -f docker-compose.yml build --pull`

3. Run the containers: `docker-compose -f docker-compose.yml up`

At this point, `localstack` will start alongside the `api` container and will be ready to mock AWS services at `http://localstack:4566`. 

## Override Default S3 Endpoint to Localstack URL

Just because you started `localstack` doesn't mean AWS services are automatically mocked. Your applications will need to override the `endpoint_url` for **every** boto3 client call you wish to mock.

- Set the envrionment variable `AWS_ENDPOINT_URL` for your API application in `docker-compose.yml`. 
```yml
AWS_ENDPOINT_URL: http://localstack:4566
```
- Pull `AWS_ENDPOINT_URL` into your application settings
```python
AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", None)
```
- Override the boto3 client `endpoint_url` to point to your localstack container
```python
client = boto3.client('s3', endpoint_url=settings.AWS_ENDPOINT_URL)
```
- All calls to `s3` will now go to your localstack container. 

You **must** override the `boto3` client for **each** AWS service that you wish to mock.

## Changing the Hostname for Localstack Container

The `hostname` of the localstack container is determined by:

- The alias name of the `services` block running the `localstack` image. (`localstack` in this case)
```
    version: "3.8" 
    services:
        localstack:  # <---- Alias name used to call the localstack container
            image: localstack/localstack
```
- The Environment Variable `HOSTNAME_EXTERNAL` on the `localstack` image. 

The localstack `hostname` is how other containers in your `docker-compose` network will communicate to your localstack container.


## Overall Benefits of Localstack

- Developers can spin up a fully localized enviornment
- Less $$ spent provisioning and cleaning up AWS
- Isolated developer environments

I hope this guide helps you quickly orchestrate localstack next to your existing applications!


- Miguel Lopez