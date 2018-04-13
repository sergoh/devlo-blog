Title: Managing Envrionments on Serverless Framework
Date: 2018-04-02
Modified: 2018-04-02
Tags: serverless, lambda, aws, java, cloud
Slug: serverless-environments
Author: Miguel Lopez
Summary: Learn how to deploy Lambda functions to dev/test/stage/prod environments on Serverless Framework

Technical Stack: AWS Lambda, Java 8 
Read: 10 minutes 

## **Prerequisites** 

- Java 8 Runetime Installed [Oracle Download](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
- Serverless Framework Installed [Serverless Quick Start](https://serverless.com/framework/docs/getting-started/)
- AWS Free Tier Account [AWS Sign Up](https://aws.amazon.com/free/)

Check out the [AWS Lambda Documentation](https://aws.amazon.com/lambda/) if you're new to AWS Lambda and serverless technology.

## **Introduction**

AWS Lambda is one of the hottest services out on the market right now. First introduced in November 2014, it has completely revolutionized the way developers develop and deploy cloud-first services and applications. Here are some of the immediate benefits of Lambda functions:

- Run code without servers
- Automatically scales code without any configuration
- Get charged per 100ms of execution time

By the end of this post, you will learn to manage and deploy AWS Lambda functions to dev/test/stage/prod environments using the Serverless framework as your deployment tool. 

## **Serverless Framework**

The Serverless Framework should **not** to be confused with _Serverless Technology_, the name commonly used to describe Function-as-a-Service technology. **The Serverless Framework is a CLI-tool you can install to help you deploy and manage your serverless functions.**

Serverless is my #1 choice for deplying lambda functions because: 

- It supports all major cloud providers. Serverless framework deploys to AWS, Azure, Google, etc. (No vendor lock-in)
- YML based instructions that deploy infrastructure-as-code
- Large developer community with dozens of plugins [Github Repo Plugins](https://github.com/serverless/plugins)

Serverless Framework uses a serverless.yml file to deploy your functions to a cloud provider. 

Here is a basic example:

```yml
service: aws-java-simple-http-endpoint

frameworkVersion: ">=1.2.0 <2.0.0"

provider:
  name: aws
  runtime: java8
  
package:
  artifact: build/distributions/aws-java-simple-http-endpoint.zip

functions:
  currentTime:
    handler: com.serverless.Handler
    events:
      - http:
          path: ping
          method: get
```

If you haven't deployed a function with Serverless yet, I'd recommend taking a few minutes to deploy their boilerplate function [here](https://serverless.com/framework/docs/providers/aws/guide/quick-start/).

## **Building Environments in Serverless**

A creative way to build environments on your serverless.yml file is to take advantage of the serverless variable system. The Serverless variable system allows you to reference other yml files by loading them into a variable. This will be the bread and butter of the pattern i'm about to show you.

For example: 
```yml
custom:
  configFile: ${file(./config/${self:provider.stage}.yml)}

provider:
  name: aws
  runtime: java8
  stage: ${opt:stage, 'dev'}
  region: 'us-east-2'
  profile: personal

  vpc: ${self:custom.configFile.vpc}
```

- if ```sls deploy --stage prod``` is ran, the ```provider.stage``` variable in the yml will be set to ```prod```
- ```${self:provider.stage}``` resolves to ```prod ```
- ```prod``` is then used in ```${file(./config/${self:provider.stage}.yml)}```
- ```${file(./config/prod.yml)}``` and loaded into the ``custom.configFile`` variable
- ```${self:custom.configFile.vpc}``` will load the ```vpc``` variable from the ```prod.yml``` file loaded into ```custom.configFile```

Likewise, if you ran ```sls deploy --stage test```, the stage variablle would be set to ```test``` and the ```test.yml``` would be loaded into ```custom.configFile```. 

## **Organizing your environmentfiles** 

I'd recommend laying out your files in the following pattern:

```
| configs 
| - dev.yml
| - test.yml
| - stage.yml
| - prod.yml
| - dr.yml
| src 
| - main
| - - java
| - - - net.app.lambda
| - - - - example
| - - - - - ExampleHandler
| serverless.yml
```

A typical config file will look like this:

_dev.yml_
```yml
region: "us-east-2"

APNS_BASE_ARN: ${ssm:/NONPROD/services/sns-apns-development}
GCM_BASE_ARN: ${ssm:/NONPROD/services/sns-gcm-development}

KMS_KEY: ${ssm:/NONPROD/security/default-kms-key}
ELASTICACHE_CONFIGURATION_ENDPOINT: ${ssm:/DEV/services/memcached/connection-url}
MEMCACHED_DEFAULT_TTL_VALUE: "604800"
```
This allows you to define different regions per {stage}.yml. You have the flexibility to set different values for different variables. You could decide that the ```MEMCACHED_DEFAULT_TTL_VALUE:``` needs to be ```172800``` in PROD as opposed to the ```604800``` in DEV. You could call different SSM values or even define different VPC Security Groups and Subnets. 

This pattern gives you a clear-readable format for your environment config files that are loaded into the parent ```serverless.yml``` file. 

Here is a general ```serverless.yml``` that will use the following ```dev.yml``` file. 

```yml
service: aws-java-sample

frameworkVersion: ">=1.2.0 <2.0.0"

custom:
  configFile: ${file(./config/${self:provider.stage}.yml)}

provider:
  name: aws
  runtime: java8
  stage: ${opt:stage, 'dev'}
  region: ${self:custom.configFile.region}
  profile: personal

  versionFunctions: false
  logRetentionInDays: 30

  environment:
        APNS_BASE_ARN: ${self:custom.configFile.APNS_BASE_ARN}
        GCM_BASE_ARN: ${self:custom.configFile.GCM_BASE_ARN}

        ELASTICACHE_CONFIGURATION_ENDPOINT: ${self:custom.configFile.ELASTICACHE_CONFIGURATION_ENDPOINT}
        MEMCACHED_DEFAULT_TTL_VALUE: ${self:custom.configFile.MEMCACHED_DEFAULT_TTL_VALUE}
```

The ```APNS_BAS_ARN```, ```GCM_BASE_ARN```, ```ELASTICACHE_CONFIGURATION_ENDPOINT```, and ```MEMCACHED_DEFAULT_TTL_VALUE``` variables are loaded from the ```custom.configFile``` file we loaded earlier with ```sls deploy --stage {env}```.

_Tip: ```${opt:stage, 'dev'}``` just means to use the text passed in after the ```--stage``` cli argument. If no ```--stage``` argument is used then default to ```dev```._ 

### **Conclusion**

I've found this file pattern to be extremely useful for defining my AWS resources throughout serverless.yml. It gives me full control over what I'm passing to the serverless.yml file for each of my lambda environments. 

You can find an example of the config pattern i've discussed [here](https://github.com/lopezm1/java-aws-template/tree/master/app-lambda).


