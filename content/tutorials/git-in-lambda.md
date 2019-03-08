Title: Running Git in AWS Lambda Functions
Date: 2019-03-07
Modified: 2019-03-07
Tags: serverless, lambda, aws, python, cloud, layers
Slug: git-in-aws-lambda
Author: Miguel Lopez
Summary: Use GitPython w/ a Git Executable in AWS Lambda

Technical Stack: AWS Lambda, Python 3.7, Serverless 
Read: 5 minutes

## **Prerequisites** 

- Serverless Framework Installed [Serverless Quick Start](https://serverless.com/framework/docs/getting-started/)
- AWS Free Tier Account [AWS Sign Up](https://aws.amazon.com/free/)
- Check out the [AWS Lambda Documentation](https://aws.amazon.com/lambda/) if you're new to AWS Lambda and serverless technology.
- Check out [GitPython](https://github.com/gitpython-developers/GitPython) - a python package used to interact w/ git repositories.

## **Introduction**

_This post builds on my previous [post](http://www.devlo.io/serverless-environments.html) on building AWS lambdas with serverless framework._

I've been tinkering around with AWS Lambda Functions a lot at work. My latest project has me exploring the possibility of 
running **Terraform**, **Terragrunt** and **git** in an AWS Lambda function. 

My purpose for this project was simple. 

- Download github projects from Python
- Store project code in the `/tmp/` folder of Lambda containers
- Allow me to create PRs, commits, etc from a lambda

In this tutorial, i'm mainly going to focus on the problems I encountered while getting **GitPython** to work in AWS Lambda w/ Python runtimes. 


## **GitPython**

**GitPython** is a library built on git commands, therefore, it requires the git binary to be installed.

Install it in your python package by running the following pip command or including it in your requirements file. 

```angular2html
pip install GitPython
```

## **First Issues**

Here was my initial lambda function as defined in my `serverless.yml`:

```yml
  run-git:
    handler: src/handler/run_git.lambda_handler
    name: ${self:provider.stage}-${self:service}-git
    description: run git commands from lambda
    memorySize: 256
    timeout: 30
``` 

The lambda handle at `run_git.lambda_handler` ran the following python code:

```angular2html
from git import Repo

def lambda_handler(event, context):

    project_name = event['github_project']
    org = event['github_org']
    git_url = "https://github.com/%s/%s" % (org, project_name)
    print("Downloading repo from %s............" % git_url)
    repo = Repo.clone_from(git_url, '/tmp/%s' % project_name)
```

The code was simple, it would download a github project and store it in the `/tmp/`.

Should have been easy until I ran into this error:

```angular2html
Unable to import module 'src/handler/run_git': Failed to initialize: Bad git executable.
The git executable must be specified in one of the following ways:
    - be included in your $PATH
    - be set via $GIT_PYTHON_GIT_EXECUTABLE
    - explicitly set via git.refresh()

All git commands will error until this is rectified.

This initial warning can be silenced or aggravated in the future by setting the
$GIT_PYTHON_REFRESH environment variable. Use one of the following values:
    - quiet|q|silence|s|none|n|0: for no warning or exception
    - warn|w|warning|1: for a printed warning
    - error|e|raise|r|2: for a raised exception

Example:
    export GIT_PYTHON_REFRESH=quiet
```  

Looking for a quick solution; I immediately put `GIT_PYTHON_REFRESH=quiet` in to the `ENVIRONMENT` variables section of my Lambda function. 

That resulted in:

```angular2html
Cmd('git') not found due to: FileNotFoundError('[Errno 2] No such file or directory: 'git': 'git'')
  cmdline: git clone -v https://github.com/hearsaycorp/hearsay-messages /tmp/hearsay-messages: GitCommandNotFound
Traceback (most recent call last):
  File "/var/task/src/handler/run_terraform.py", line 13, in lambda_handler
    download_hearsay_repo(repo_name, git_hash)
  File "/var/task/src/utils/github_utils.py", line 16, in download_hearsay_repo
    repo = Repo.clone_from(git_url, '/tmp/%s' % project_name)
  File "/var/task/git/repo/base.py", line 988, in clone_from
    return cls._clone(git, url, to_path, GitCmdObjectDB, progress, **kwargs)
  File "/var/task/git/repo/base.py", line 933, in _clone
    v=True, universal_newlines=True, **add_progress(kwargs, git, progress))
  File "/var/task/git/cmd.py", line 548, in <lambda>
    return lambda *args, **kwargs: self._call_process(name, *args, **kwargs)
  File "/var/task/git/cmd.py", line 1014, in _call_process
    return self.execute(call, **exec_kwargs)
  File "/var/task/git/cmd.py", line 738, in execute
    raise GitCommandNotFound(command, err)
git.exc.GitCommandNotFound: Cmd('git') not found due to: FileNotFoundError('[Errno 2] No such file or directory: 'git': 'git'')
```

That error made it clear to me. AWS Lambda functions did not come bundled with `git` executables in the runtime container. Therefore, **GitPython** 
could not run commands against `git` in the container's `$PATH`. 

## **Next Issues**

I thought alright, simple, how hard could it be to install `git` on the `$PATH`. 

Turned out to be pretty tough. I looked all over the internet and stumbled onto the following article by [cloudbriefly.com](https://cloudbriefly.com/post/running-git-in-aws-lambda/#appendix-b-how-to-clone-a-git-repository-in-aws-lambda-python). 
At first glance, it seemed way too complicated. However, the more I read it, the more it made sense.

I figured I'd give it a shot and run their python code before running `GitPython` code. 

I downloaded the `git` binary from Amazon Repositories and added the `/tmp/` path to my `$PATH`.

Still this resulted in: 
```angular2html
git.exc.GitCommandNotFound: Cmd('git') not found due to: FileNotFoundError('[Errno 2] No such file or directory: 'git': 'git'')
```

## **Solution**

I was about to give up when I stumbled upon the following [Lambda Layer](https://github.com/lambci/git-lambda-layer).

This Lambda Layer promised to include the binaries for `ssh` and `git` regardless of the lambda runtime. 

I had never used Lambda Layers before but remember attending a session about them at AWS re:Invent. 

(Read about Lambda Layers [here](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-use-any-programming-language-and-share-common-components/))

Seemed too simple. I had searched the internet for hours on a solution for installing git on AWS Lambda Functions. 

I included the layer in my `serverless.yml` file like so:

```yml
  run-git:
    handler: src/handler/run_git.lambda_handler
    name: ${self:provider.stage}-${self:service}-git
    description: run git commands from lambda
    memorySize: 256
    timeout: 30
    layers:
      - arn:aws:lambda:us-west-2:553035198032:layer:git:5
```

I deployed my function and BOOM! It worked. Just like that. My lambda function now included a ~layer~ that would allow me to use the `git` binary. So simple. Now I could play
around with `git` in my lambda functions.

## **Conclusion**

This should help you install `git` on AWS Lambda functions and use the **GitPython** python package.

PM me on LinkedIn if you have any questions! Info should be located on the left.

-- Miguel Lopez