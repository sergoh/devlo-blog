Title: Jenkins Pipeline Env Variables w/ AWS SSM
Date: 2018-04-12
Modified: 2018-04-12
Tags: jenkins, aws, cloud, groovy, automation, ssm
Slug: ssm-env-jenkins
Author: Miguel Lopez
Summary: Pull environment variables from AWS Parameter Store in a Jenkins Declarative Pipeline


Technical Stack: AWS Parameter Store, Jenkins, Jenkinsfile, Shell

## **Introduction**

By the end of this article, you should understand how to use AWS Parameter Store (SSM) to pull down environment variables in your Jenkins Declarative Pipeline.

I recommend heading over to the [Jenkins Pipeline documentation](https://jenkins.io/doc/book/pipeline/syntax/) if you've never heard of a Jenkinsfile. Writing your job as a Jenkinsfile is also known as _Jenkins-as-code_ because it allows you to check your Jenkins job into source control. It allows you to version your build jobs and port them to other Jenkins boxes.

## **Jenkins Credentials Store**

For the regular Jenkinsfile creators out there, you might be asking me why i'm using AWS Parameter Store to fetch credentials when Jenkins already has a [credentials](https://jenkins.io/doc/book/pipeline/jenkinsfile/#handling-credentials) store that looks something like this....


```
pipeline {
    agent {
        // Define agent details here
    }
    environment {
        AWS_ACCESS_KEY_ID     = credentials('jenkins-aws-secret-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('jenkins-aws-secret-access-key')
    }
}
```

The answer is simple: portability of Jenkins jobs. I wanted to remove the dependency of my Jenkinsfiles depending on the credentials store on my Jenkins box being loaded up with parameters. 

I've seen some teams solve this issue by checking the environment variables into source control directly. 

```
pipeline {
    agent any
    environment { 
        env = 'stage'
        secret = 'xxxxxxxxxxxxxxxx'
    }
}
```
However this isn't any better because it encourages you to possibly explose environment secrets or configurations via source control.

## **AWS SSM**

About a year ago, my team decided to standardize a majority of our application configurations and secrets on the [AWS Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html)

This led me to explore the idea of loading SSM variables into my environment block on the Jenkinsfile. AWS Parameter Store has worked fantastically for us. We use it with Saltstack, in our main applicaton and shell script files throughout the automation toolchain. It only made sense that I would try to extend SSM to our Jenkinsfile. 

In order for this to work, it's important to note that your Jenkins box will need two things. 

- IAM Role attached with permissions to AWS SSM and any KMS decryption keys
- AWS CLI installed on the box

Here's how SSM looks in enviornment variables: 

```
environment {
        SECRET_ACCESS_KEY = '$(aws ssm get-parameters --region $REGION --names /jenkins/nonprod/iam-role-secret --query Parameters[0].Value --with-decryption | sed \'s/"//g\')'
        ACCESS_KEY_ID = '$(aws ssm get-parameters --region $REGION --names /jenkins/nonprod/iam-role-key --query Parameters[0].Value --with-decryption | sed \'s/"//g\')'
    }
```

Pretty simple right? Here you can see that the CLI commands are being loaded into `SECRET_ACCESS_KEY` and `ACCESS_KEY_ID`. It's important to note that the CLI commands will not be executed until they are run in a `sh` command in the `stages` section of your pipeline. 

Including the enviornment variables throughout your pipeline is easy. 

```
stages {
        stage ('Initialize VPC') {
            steps {
                dir('terraform'){
                    sh """
                    serverless config credentials --provider provider --key ${env.ACCESS_KEY_ID} --secret ${env.SECRET_ACCESS_KEY}
                    """
                }
            }
        }
```

There are two important things to note here. 

1. It's important to use `"`. Double quotes is our way of signifying that this is a groovy string.
2. You must use the `${env.VARIABLE}` syntax to get variables from the envrionment section.

In the previous example, you can see that we are exporting AWS Secret Keys and AWS Access Keys so that the Serverless CLI can use the credentials. It should be noted that the CLI Commands are being evaluated on the fly. This means that a string containing the AWS SSM CLI Command is loaded from the `environment` block, the command is ran, and the result is then loaded into the CLI command. The CLI command from the `enviornment` block is **NOT** ran until it is called within the `sh` command. 

Using AWS SSM in our Jenkinsfile has been awesome because it allows our pipeline to remain flexibile. My cloud team only has to remember to update ther Jenkins IAM role key and secret in one location should they ever choose to rotate it. 

## **Conclusion**

At the end of the day, using the AWS SSM Store helps my team move towards their goal of having all infrastructure-as-code. It also standarizes our parameters on the AWS Parameter store so that application secrets aren't scattered all over the place. 