Title: Managing Automation Around Auto Scaling Groups
Date: 2018-03-31
Modified: 2018-03-31
Tags: saltstack, aws, cloud, EC2, automation, codedeploy
Slug: asg-automation-toolset
Author: Miguel Lopez
Summary: How to pick an automation toolset that supports auto scaling in the cloud


Technical Stack: AWS EC2 (AWS AMI CentOS), SaltStack (2018.7.X), CodeDeploy  
Read: 10 minutes 

## **Introduction**

There are 4 key components when it comes to creating stateless servers for an autoscaling groups (ASGs). 

- Automatic Configuration Management (SaltStack, Chef, Puppet, AWS OpsWorks) 
- Automatic Code Deployment to New VMs that Spawn (CodeDeploy) 
- Bootstrapping Minions as they Spawn
- CI/CD Pipelines (Jenkins, VSTS, Code Pipelines, etc) 

Having these 4 components will help you achieve an automated and repeatable way of creating VMs from the ground up. This will allow you to create and register new nodes with a load balancer should the demand go up. 

There’s no perfect formula when it comes to selecting the right set of tools for the job. The main thing that matters is that you select a set of tools that’ll help your organization successfully manage an autoscaling group. 

## **Configuration Management**

These tools allow you to manage differences across different applications and environments in your infrastructure. You can manage different configuration files, symlinks, create/delete different users, web hosts files, etc. It allows you to remove “hard coding” from VMs so that you can easily produce a “production API server” or a “DEV www server”.

Choosing the right configuration management tool typically boils down to choosing a tool that makes sense for your organization. I’ve been a huge fan of SaltStack because it’s declarative, meaning that order in which states are executed doesn't matter. 

## **Automatic Code Deployment**

This is important because if your ASG group ever needs to scale up another node, you need to find a way to deploy code to it without having to manually trigger a build. 

I’ve had great success accomplishing this with CodeDeploy. CodeDeploy is an AWS service that uses .yml based instructions in order to install an application on a VM. Here’s an example:

```yml
version: 0.0
os: linux
files:
  - source: /app
    destination: /var/www/html/WordPress
 - source: /backend
    destination: /var/www/backend/service
hooks:
  BeforeInstall:
    - location: scripts/install_dependencies.sh
      timeout: 300
      runas: root
  AfterInstall:
    - location: scripts/change_permissions.sh
      timeout: 300
      runas: root
  ApplicationStart:
    - location: scripts/start_server.sh
    - location: scripts/create_test_db.sh
      timeout: 300
      runas: root
  ApplicationStop:
    - location: scripts/stop_server.sh
      timeout: 300
      runas: root
```

It comes complete with life cycle events, the power to run shell scripts and even allows you to install code in multiple locations. 

It should always be your goal to minimize downtime during deployments (Zero downtime if possible). CodeDeploy supports this with A/B deployments or One-At-A-Time deployments.

## **Bootstrapping Minions**

Find a way to hook and tie a VM to the rest of your infrastructure. This is where you typically notify your configuration management tool and code deployment tool that your freshly created VM is alive and well. 

I've shared how to do this in another post [Automate Salt-Minion Registrations on EC2](http://www.devlo.io/bootstrap-salt.html#bootstrap-salt)

## **CI/CD**

It’s best to find a tool that’ll push changes to your deployment group (fleet of VMs) while also registering that a new build has been released. It’s important for your automation toolset register that a new build has been released. This will guarantee that your ASG will always install the latest version of your application.\

## **Personal Experience** 

I’ve personally had great success with the following tech stack:

- AWS EC2
- Jenkins
- CodeDeploy
- SaltStack

EC2 instances allow you to define a cloud-init script. Cloud-init scripts are scripts that are automatically ran once when the VM is created. This allows me to register each VM that comes online with SaltStack and CodeDeploy. 

Jenkins Is a great CI/CD tool to kick off builds from. Its allows me to pull down my code from GitHub, trigger a build process, run automation tests, push to static code analysis and finally deploy the build to a deployment group via CodeDeploy. 

From this point, CodeDeploy will begin installing the build on the requested deployment group. This can either be a single VM or an ASG. CodeDeploy is such a powerful installation Daemon because automatically registers your latest build pushed to it by a CI/CD tool. This ensures that my ASG will always receive the latest build without me having to worry about it. 

SaltStack has been crucial when it comes to influencing how my team designs code. We’ve done our best to start removing any/all hard coded values out of our code. Imagine if a customer needed you to change an integration URL for their prod server. With Salt, we are able to just change the config file and push out the newest state. This is so much easier than changing our code base, scheduling a time for a release, and pushing out the new build. Not to mention safer too. 

## **Conclusion**

Over the next few weeks I’ll be hoping to add some more posts that dive a little bit deeper into this topic.

- [Automate Salt-Minion Registrations on EC2](http://www.devlo.io/bootstrap-salt.html#bootstrap-salt)
- _Introduction to Salt-Master_
- _Organizing States on Salt-Master_
- _Introduction to CodeDeploy_