Title: Serverless Framework Guide: Creating a Serverless RDS Cluster
Date: 2023-06-10
Modified: 2023-06-10
Tags: serverless, lambda, aws, python, cloud, developer, django, python, rds, serverless-framework, guide, python3.9, postgres, mysql, aurora, serverless-rds, serverless-rds-cluster
Slug: sls-framework-guide-creating-serverless-rds-cluster
Author: Miguel Lopez
Summary: A guide to help you deploy serverless RDS clusters using the Serverless Framework. By the end of this guide, you will have a serverless Postgres database created by Serverless Framework to support your Lambda Functions.

Technical Stack: AWS, Lambda, Serverless Framework, Python, RDS, MySQL

Read: 10 minutes

## Pre-Requisites

To deploy the following Serverless Framework template, you will need the following:

- An AWS account.
- AWS CLI installed locally. 
- API credentials for your AWS account configured in your AWS CLI locally by running `aws configure`.
- Serverless framework installed locally via `npm -g install serverless`.


## Creating a Serverless RDS Cluster

Using Serverless Framwework, the following example creates these resources in AWS:
- AWS::RDS::DBCluster
- AWS::SecretsManager::Secret
- AWS::SSM::Parameter

In addition to the Database, the template also creates a secret and SSM parameter to store the database password and host address. Your lambda can use these values to connect to the database.

```yml
service: derezzed-db-infrastructure

configValidationMode: error

custom:
  stage: ${opt:stage, 'dev'}

params:
  default:
    securityGroupId: [ 'sg-xxxxxxxx' ]
    DBSubnetGroupName: default-vpc-xxxxxxxxx
    db_name: derezzeddb
    master_username: derezzed

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
    AuroraDerezzedSecret:
      Type: AWS::SecretsManager::Secret
      Properties:
        Name: !Join ['/', ["${param:db_name}", "${self:custom.stage}"]]
        Description: !Join ["", ["secret for derezzed database ", !Ref "AWS::StackName"]]
        GenerateSecretString:
          SecretStringTemplate: '{"username": "${param:master_username}"}'
          GenerateStringKey: "password"
          ExcludeCharacters: '"@/\'
          PasswordLength: 16
    DerezzedDBCluster:
      Type: AWS::RDS::DBCluster
      Properties:
        MasterUsername: ${param:master_username}
        MasterUserPassword: !Join ['', ['{{resolve:secretsmanager:', !Ref AuroraDerezzedSecret, ':SecretString:password}}' ]]
        DatabaseName: ${param:db_name}
        Engine: aurora-postgresql
        EngineMode: serverless
        EnableHttpEndpoint: true
        DBClusterIdentifier: DerezzedDBCluster-${self:custom.stage}
        VpcSecurityGroupIds: ${param:securityGroupId}
        DBSubnetGroupName: ${param:DBSubnetGroupName}
        ScalingConfiguration:
          AutoPause: false
          MaxCapacity: 4
          MinCapacity: 2
    DatabaseHostParam:
      Type: AWS::SSM::Parameter
      DependsOn:
        - DerezzedDBCluster
      Properties:
        Description: "Host Address for the Derezzed DB"
        Name: "/derezzed/${self:custom.stage}/db-host"
        Type: String
        Value: !GetAtt DerezzedDBCluster.Endpoint.Address
  Outputs:
    AuroraDerezzedSecretArn:
      Value: !GetAtt AuroraDerezzedSecret.Arn
    AuroraDerezzedSecretName:
      Value: !Ref AuroraDerezzedSecret
    DatabaseHostParam:
      Value: !Ref DatabaseHostParam
    DatabaseClusterName:
      Value: !Ref DerezzedDBCluster
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

    ✔  derezzed-db-infrastructure › deployed › 219s
```

Run `sls outputs --stage dev` to see the outputs of the deployment. You'll see the following:

```bash
Running "serverless" from node_modules

derezzed-db-infrastructure:
  DatabaseHostParamName: /derezzed/dev/db-host
  DatabaseClusterName: derezzeddbcluster-dev
  AuroraDerezzedSecretName: arn:aws:secretsmanager:us-west-2:590762009186:secret:derezzeddb/dev-DldvfU
  ServerlessDeploymentBucketName: hsl-dev-serverless
```

## Connecting to the Cluster from your local machine

Once the cluster is created, you can connect to the database using the following command:

```bash
psql -h $(aws ssm get-parameter --name /derezzed/dev/db-host --query Parameter.Value --output text) -U derezzed -d derezzeddb
```

You can find the password value in Secrets Manager with the following command:

```bash
aws secretsmanager get-secret-value --secret-id derezzed/dev --query SecretString --output text
```

## Connecting to the Cluster from Lambda

To connect to the cluster from Lambda, you can use the following code:

```python
import boto3
import os
import psycopg2

password = boto3.client('secretsmanager').get_secret_value(SecretId=os.environ['SECRET_NAME'])['SecretString']
host = boto3.client('ssm').get_parameter(Name=os.environ['DB_HOST_PARAM_NAME'])['Parameter']['Value']

conn = psycopg2.connect(
    host=host
    database="derezzeddb",
    user="derezzed",
    password=password)

def handler(event, context):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        for row in rows:
            print(row)
```

Don't forget to fetch Secrets and Parameters outside of your lambda handler. This will prevent your lambda from fetching these values on every invocation. Saving you $$$$$.


## Troubleshooting Connections

If you can't connect, check the following:

- Do you have the correct security group attached to the RDS Cluster? 
- Are you invoking the CLI command from a machine that has access to the security group?