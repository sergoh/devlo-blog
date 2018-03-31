Title: Automate Salt-Minion Registrations on EC2
Date: 2018-03-30
Modified: 2018-03-30
Tags: saltstack, aws, cloud, EC2, automation
Slug: bootstrap-salt
Author: Miguel Lopez
Summary: Use scripts to automatically register new EC2 minions with Salt-Master


Automate Salt-Minion Registrations on EC2
##############

## Intro

These scripts can be used to register your salt minion to Salt-Master upon successfully launching. 

Whether you're launching single instances or launching instances as a part of an autoscaling group, I'd highly recommend using cloud-init scripts. They're easy to use and help you install all of your packages.

My scripts also include CodeDeploy. If you haven't heard of CodeDeploy, I'd take a moment to read up on it here. [AWS CodeDeploy](https://aws.amazon.com/codedeploy/)

CodeDeploy can help you with:

- repeatable deployments 
- automatic code deployments to scaled instances
- stops and rollbacks
- deployment history

## Cloud Init Script

Technical Stack: SaltStack, EC2(CentOS)

Use this as the cloud-init data for an EC2 instance. Works fanstastically with auto-scaling-groups. Recommend placing this script in a cloudformation or terraform script so that all instances are automatically launched with it. 

Installs codedeploy and automatically registers salt-minion to a salt-master.

- dynamic by region
- installs codedeploy-agent
- registers salt-minion to master
- auto-deploy your latest revision from a CodeDeploy deployment group to this instance 

```yml
#cloud-config
# Set hostname to match the instance ID, rather than the
# automatic hostname based on the IP address.
# In these three commands _GRP_ is a placeholder and
# should be changed to your Auto Scaling Group name.
bootcmd:
  # Dynamically fetch region for EC2 in aws
  - "region=$(curl http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/.$//')"
  - "sudo yum -y install ruby wget jq"
  # Install codedeploy https://aws.amazon.com/codedeploy/
  - "sudo cd /home/ec2-user"
  - "sudo wget https://aws-codedeploy-${region}.s3.amazonaws.com/latest/install"
  - "sudo chmod +x ./install"
  - "sudo ./install auto"
  - "sudo service codedeploy-agent start"
  # BOX_NAME fetches the EC2 tag for "Name" - name used to register with salt master
  - "INSTANCE_ID=$(curl http://169.254.169.254/latest/meta-data/instance-id)"
  - "BOX_NAME=$(aws ec2 describe-tags --region $region --filters \"Name=resource-id,Values=$INSTANCE_ID\" | jq '.Tags[] | select(.Key == \"Name\") | .Value' | sed s/\\\"//g)"
  # Change hostnames on VM
  - "cloud-init-per instance my_set_hostname sh -xc \"echo $BOX_NAME-$INSTANCE_ID > /etc/hostname; hostname -F /etc/hostname\""
  - "cloud-init-per instance my_etc_hosts sh -xc \"sed -i -e '/^127.0.0.1/d' /etc/hosts; sed -i -e '/^::1/d' /etc/hosts; echo 127.0.0.1 $BOX_NAME-$INSTANCE_ID >> /etc/hosts\""
  # Install and bootstrap salt-minion to saltmaster
  - "SALT_MASTER_IP={IP-TO-SALT-MASTER-HERE}"
  - "mkdir -p /etc/salt/; $BOX_NAME-$INSTANCE_ID > /etc/salt/minion_id"
  - "sudo curl -o /tmp/bootstrap-salt.sh -L https://bootstrap.saltstack.com"
  - "sudo sh /tmp/bootstrap-salt.sh -i $BOX_NAME-$INSTANCE_ID -A $SALT_MASTER_IP"
  - "sudo rm -f /tmp/bootstrap-salt.sh"
# Preserve the hostname file since we've had to manually edit it
preserve_hostname: true
# Don't let cloud-init update the hosts file since we have edited it manually
manage_etc_hosts: false
```
_You'll notice some curls to http://169.254.169.254, this is an internal API used by EC2 instances to fetch metadata about your instance_ 

*Replace $SALT_MASTER_IP with the IP of your salt-master. Don't forget to tag your EC2 instance with a "Name" tag. Naming is important when it comes to defining salt environments.*

For example:
- _stage-api_
- _stage-www_
- _test-api_
- _test-www_

These are all great examples of "Name" tags for instances because it allows you to apply salt states by '*www', '*api', 'stage*' or 'test*' or some other combination. 

This can be extremely useful for defining how you run salt commands. This naming convention would allow you to run salt commands in the following way: 

```sh
salt 'stage*' state.show_top
```

This command would only apply salt states to environments tagged with _stage_ in their name. In this example, that would mean the stage-api and stage-www server. 


## Shell Script Equivalent

Technical Stack: SaltStack, EC2(CentOS)

Installs codedeploy and automatically registers salt-minion to a salt-master. Use this script if only if you'd like your packages to be installed post-creation. 

- dynamic by region
- installs codedeploy-agent
- registers salt-minion to master

Run this as a bootstrapping script on an EC2 instance. 

```sh
# Dynamically fetch region for EC2 in aws
region=$(curl http://169.254.169.254/latest/meta-data/placement/availability-zone | sed ’s/.$//‘);

# gr8 packages
sudo yum -y install ruby wget jq;

# Install codedeploy https://aws.amazon.com/codedeploy/
sudo cd /home/ec2-user;
sudo wget https://aws-codedeploy-${region}.s3.amazonaws.com/latest/install;
sudo chmod +x ./install;
sudo ./install auto;
sudo service codedeploy-agent start;

# Name used to register with salt master
BOX_NAME=$(aws ec2 describe-tags --region $region --filters \"Name=resource-id,Values=$INSTANCE_ID\" | jq '.Tags[] | select(.Key == \"Name\") | .Value' | sed s/\\\"//g);
INSTANCE_ID=$(curl http://169.254.169.254/latest/meta-data/instance-id);

# Change hostnames on VM
echo $BOX_NAME-$INSTANCE_ID > /etc/hostname;
sed -i -e '/^127.0.0.1/d' /etc/hosts; 
sed -i -e '/^::1/d' /etc/hosts; 
echo 127.0.0.1 $BOX_NAME-$INSTANCE_ID >> /etc/hosts;

# Install and bootstrap salt-minion to saltmaster
SALT_MASTER_IP={IP-TO-SALT-MASTER-HERE}
mkdir -p /etc/salt/; $BOX_NAME-$INSTANCE_ID > /etc/salt/minion_id;
sudo curl -o /tmp/bootstrap-salt.sh -L https://bootstrap.saltstack.com;
sudo sh /tmp/bootstrap-salt.sh -i $BOX_NAME-$INSTANCE_ID -A $SALT_MASTER_IP;
sudo rm -f /tmp/bootstrap-salt.sh;
```

_You'll notice some curls to http://169.254.169.254, this is an internal API used by EC2 instances to fetch metadata about your instance_ 

Replace $SALT_MASTER_IP with your own variables.