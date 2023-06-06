Title: Exporting AWS SSO Login Credentials
Date: 2023-06-05
Modified: 2023-06-05
Tags: aws, aws-cli, sso, login, credentials, docker, docker-compose, single-sign-on, bash, aws-sso
Slug: exporting-aws-sso-login-credentials
Author: Miguel Lopez
Summary: Exporting AWS SSO Login Credentials to Bash and Docker

Technical Stack: AWS CLI, Single Sign On, Docker, Docker-Compose, Bash

Read: 5 minutes

## Introduction

This page applies to you if your organization uses `aws sso login` to fetch local AWS credentials. 

After reading this, you will be able to:

- Export AWS SSO Login Credentials to Bash
- Export AWS SSO Login Credentials to Docker run commands
- Export AWS SSO Login Credentials to Docker Compose

https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sso/login.html

### Log into AWS SSO

Access your local AWS SSO login credentials by running the following command:

```bash
aws sso login --profile example-profile
```

Your terminal will output the following:
```bash
Attempting to automatically open the SSO authorization page in your default browser.
If the browser does not open or you wish to use a different device to authorize this request, open the following URL:

https://device.sso.us-west-2.amazonaws.com/

Then enter the code:

XXXX-XXXX
Successfully logged into Start URL: https://x-xxxxxxxxxx.awsapps.com/start
```

### Export AWS SSO Login Credentials to Bash

After running `aws sso login`, automatically export your credentials to bash by running the following command:

```bash
eval "$(aws configure export-credentials --profile example-profile --format env)"
```

Verify your credentials are working by running the following command:

```bash
env | grep AWS
```

You can also run a test command like `aws s3 ls` to verify your credentials are working.

### Export AWS SSO Login Credentials to Docker run commands

After running `aws sso login`, automatically export your credentials to a file by running the following command:
```bash
aws configure export-credentials --profile aws-dev --format env-no-export > .env.docker
```

This creates a file called `.env.docker`. This file can then be passed to the `docker run` command combined with `--env` as follows:

```bash
docker run --env-file .env.docker --rm -it alpine:latest sh
```

This will grant your local container access to AWS resources using the credentials from your AWS SSO login.

### Export AWS SSO Login Credentials to Docker Compose

After running `aws sso login`, automatically export your credentials to a file by running the following command:
```bash
aws configure export-credentials --profile aws-dev --format env-no-export > .env.docker
```

This creates a file called `.env.docker`. This file can then be passed to the `env_file` section of a `docker-compose.yml` file as follows:

```yml
version: "3.8"
services:
  alpine:
    image: alpine:latest
    env_file:
      - .env.docker
```

This will grant your local container access to AWS resources using the credentials from your AWS SSO login.