Title: Dockerfile with Packer and Ansible Installed
Date: 2023-06-06
Modified: 2023-06-06
Tags: docker, packer, ansible, devops, cicd, docker-compose, automation, bash, hashicorp, ami, aws, machine-image, infrastructure-as-code, images, img, dockerfile, github, github-actions, actions
Slug: create-docker-image-with-packer-and-ansible
Author: Miguel Lopez
Summary: Create a Docker Image with Packer + Ansible installed. This is useful for creating a Docker Image that can be used for CI/CD pipelines.

Technical Stack: Docker, Packer, Ansible

## Introduction

The goal of this tutorial is to create a Docker Image with Packer and Ansible installed. 

This image can be used to execute Packer and Ansible builds in a CI/CD pipeline.

### Create Dockerfile

Create a file named `Dockerfile` with the following contents:

```dockerfile
FROM hashicorp/packer

USER root

RUN apk add -v --update --no-cache aws-cli ansible jq openssh bash curl py3-boto3 sudo

# Copy Packer Arifacts
COPY . .

# Clean up apt
RUN rm -rf /tmp/* && \
    rm -rf /var/cache/apk/* && \
    rm -rf /var/tmp/*
```

### Sample Packer HCL File

This Dockerfile is optimized to help you run Packer builds with the `ansible` provisioner. Something similar to the `build` section below:

```hcl
source "amazon-ebs" "ubuntu" {
    ...
}

build {
  name = "packer-build"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]

  provisioner "ansible" {
    user = "ubuntu"
    playbook_file = "./playbook.yml"
    ansible_env_vars = ["ANSIBLE_PIPELINING=true", "ANSIBLE_SSH_PIPELINING=true"]
    use_proxy = false
    extra_arguments = [
      "--become", "--become-method=sudo"
    ] 
  }
}
```

# Build Docker Image and Run Locally

You can run the following command to build your Docker Image locally:

```bash
docker build -t packer-ansible .
```

You can run the following command to execute your Packer + Ansible build:

```bash
docker run --rm -it \
  --env-file ~/.aws/credentials \
  packer-ansible build base-images.pkr.hcl
```

`--env-file` is optional for passing AWS credentials to your Docker container.

### Using Image in CI/CD

We use these images to speed up our automated packer builds. Otherwise, it will take you long time to install packer + ansible on every build. 

Here is an example of CircleCI config that uses this image:

```yaml
jobs:
  build-base-ami:
    description: >
      Build Packer base AMIs.
    resource_class: small
    docker:
      - image: xxxxxxxx.dkr.ecr.us-west-2.amazonaws.com/base-ami-builder:latest
        aws_auth:
          aws_access_key_id: $AWS_ACCESS_KEY_ID
          aws_secret_access_key: $AWS_SECRET_ACCESS_KEY
    steps:
      - checkout
      - run:
          name: Build AMI
          no_output_timeout: 30m
          command: |
            packer init base-images.pkr.hcl
            packer validate base-images.pkr.hcl
            packer build base-images.pkr.hcl
```