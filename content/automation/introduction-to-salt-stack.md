Title: Introduction to SaltStack
Date: 2018-03-22
Modified: 2018-03-22
Tags: saltstack, aws, cloud
Slug: my-super-post
Author: Miguel Lopez
Summary: a story of how Salt Master revolutionized the way my organization manages infrastructure, has identical environments and keeps cloud engineers mentally SANE


_Technical Environment: SaltStack v1.2123, AWS EC2 (CentOS ami)_

_Difficulty: Easy_

## **Introduction to SaltStack**

TLDR; SaltStack rocks. Let Salt manage your infrastructure and you’ll look like a hero.

Configuration Management (as it pertains to software infrastructure) is this idea that you have a central node or tool that is responsible for managing the state of each individual node throughout your infrastructure. It makes your life 100% easier by automating startup scripts, ssh-key placement, symlinks, config files and much much more. 

Have you ever found yourself in a situation where you’re constantly having to repeat the same tasks on a single VM or fleet of VMs? If so, then configuration management is probably something you need. 

In this post, I’ll cover a few topics:
- Introduction to SaltMaster
- How to create a salt master node
- How to connect a salt minion to the master node
- How to push states from the salt master to the minion

Fair warning, all of this article covers how to use SaltStack in an AWS EC2 environment. It should be noted that SaltStack would work perfectly well on Azure, GCM, or any other datacenter model. 

## **Key Terms**

**Salt-Master:** node used control your salt-minions accross your infrastructure. Salt-masters will push a desired state down.

**Salt-Minion:** node that is controlled by a Salt-Master.

**Salt-State:** a set of instructions passed down to a node. Could be anything from placing an SSH key, downloading yum packages or removing users access.

## **Installing Salt-Master**

_I'll assume you know how to create an EC2 instance and SSH inside_ 

1. Launch EC2 Linux AMI and SSH inside

```
ssh ec2-user@10.0.2.254 -i privatekey.pem
```

2. Use Salt bootstrap script to install the Salt-Master agent

```
[root@salt-master ~]# cd /home/ec2-user
[root@salt-master ~]# curl -o bootstrap-salt.sh -L https://bootstrap.saltstack.com
[root@salt-master ~]#sudo sh bootstrap-salt.sh -M -N
```

3. Verify Salt-Master exists

```
[root@salt-master ~]# salt-master --version
salt-master 2018.3.0 (Oxygen)
```


## **Installing Salt-Minions**

1. Create salt directory and the minion_id file
```
sudo -i;
mkdir -p /etc/salt/; 
echo "dev-minion-01" > /etc/salt/minion_id;
```

2. Use Salt bootstrap script to install the Salt-Minion agent
```
cd /home/ec2-user;
curl -o /tmp/bootstrap-salt.sh -L https://bootstrap.saltstack.com;
sh /tmp/bootstrap-salt.sh -i dev-minion-01 -A 10.0.2.254;
```
- `-i` flag is used to pass the name of the minion
- `-A` flag is the IP of the Salt-Master node you wish to register to

3. Verify the Salt-Minion exists

```
[ec2-user@ip-10-0-1-31 ~]$ salt-minion --version
salt-minion 2018.3.0 (Oxygen)
```

## **Accept Salt-Minion**

1. Head back over to the Salt-Master and check if the key is listed.
```
[root@salt-master ~]# salt-key -L
Accepted Keys:
Denied Keys:
Unaccepted Keys:
dev-minion-01
Rejected Keys:
```

2. By this point you should see your minion key. Accept the key to put it under the Salt-Master's control.

```
[root@salt-master ~]# salt-key -a dev-minion-01
The following keys are going to be accepted:
Unaccepted Keys:
dev-minion-01
Proceed? [n/Y] y
Key for minion dev-minion-01 accepted.

[root@salt-master ~]# salt-key -L
Accepted Keys:
dev-minion-01
Denied Keys:
Unaccepted Keys:
Rejected Keys:
```
At this point, your salt-master should be able to communicate to your salt-minion and vice-versa. 

_If you do not see the salt-minion key appear after a minute, head back over to your salt-minion box and run `salt-minion debug`_

```
[ERROR   ] The Salt Master has cached the public key for this node, this salt minion will wait for 10 seconds before attempting to re-authenticate
[ERROR   ] The Salt Master has cached the public key for this node, this salt minion will wait for 10 seconds before attempting to re-authenticate
[ERROR   ] The Salt Master has cached the public key for this node, this salt minion will wait for 10 seconds before attempting to re-authenticate
```
If you see the following error, it means your salt-master and salt-minion might not be able to communicate. Ensure that port 4505-4506 are open between the two instances. 

_Here is how I configured my SG in Terraform_
```
resource "aws_security_group" "sg_salt_stack" {
  name = "sg_salt_stack"
  vpc_id = "${aws_vpc.sample-cloud-vpc.id}"

  ingress {
    from_port = "4505"
    to_port = "4506"
    protocol = "tcp"
    self = true
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name = "sg_salt_stack"
  }
}
```
## **Configure First Salt State**

Head back over to Salt-Master. First things first, explore what's in side the /etc/salt folder. This is where the Salt-Master configuration files will live. 

1. Archive the premade configuration file located at `/etc/salt/master`. This file is full of instructions and definitions. It's useful to read but hard to maintain, therefore we will keep it around but create our own. 

```
[root@salt-master salt]# mv /etc/salt/master /etc/salt/master.orig
```

2. Create your own `/etc/salt/master` and define the bare minimum.

```
timeout: 60
worker_threads: 10
ipv6: False
log_level_logfile: debug
presence_events: true

# Master file_roots configuration:
file_roots:
  base:
    - /srv/salt/base

default_include: master.d/*.conf

pillar_roots:
  base:
    - /srv/pillar

module_dirs:
  - /srv/salt/_modules
  - /srv/salt/extmods
```

For the sake of this tutorial, we will only be covering a state that lives in our `/srv/salt/base` file root. I will not be going `modules`, `pillars`, or `node_groups` just quite yet and will leave those for another post. 

3. Our first state will live in our `base` environment. Go ahead and create a folder in the `/srv/salt/base` location. 

```
[root@salt-master salt]# cd /srv/
[root@salt-master srv]# mkdir salt
[root@salt-master srv]# cd salt/
[root@salt-master salt]# mkdir base
[root@salt-master salt]# cd base
[root@salt-master base]# pwd
/srv/salt/base
```
This will be known as our `base` enviornment. `Base` environments are typically states that are applied across your each `dev`/`test`/`stage`/`prod` environment. I'll also cover how to create environment specific states in a future post. 

4. Create a `/srv/salt/base/touch-file` folder. 

```
[root@salt-master base]# mkdir touch-file
[root@salt-master base]# vi init.sls
[root@salt-master base]# pwd
/srv/salt/base
```
This folder will contain our first state that will create a "Hello World" text file on our minion. 

5. Inside the `touch-file` folder, create an `init.sls` file. Every folder must have an `init.sls` file. This file will contain the instructions for your state.

```
[root@salt-master base]# vi init.sls
```
6. Paste the following text inside. It's important to note that each `.sls` file is yml based. **This means that spacing and tabs matter.**

```
/tmp/hello-world.txt:
  file.managed:
    - source:
      - salt://touch-file/hello-world.txt
```
This state tells our salt-master to create a file at `/tmp/hello-world.txt` on our salt-minion box. As a `file.managed` state, it will create or replace the `hello-world.txt` file whenever it does not match the `hello-world.txt` file on the salt-master server. 

Be sure to read all about salt-states [on their official documentation](https://docs.saltstack.com/en/latest/contents.html)

7. Create the `hello-world.txt` file at `/srv/salt/base/touch-file`

```
[root@salt-master base]# echo "hello world" > hello-world.txt
```
This satisfies the `source` requirement defined our in `init.sls` file. 

8. The last thing we need to do is create the `top.sls` file. We will need to `cd` back to our `/srv/salt/base`. And create it there. 

```
[root@salt-master base]# vi top.sls
```
Paste the following text inside. 

```
base:
  '*':
    - touch-file
```
The `top.sls` file will apply the `touch-file` state we just created to all salt-minions under our control. 

`top.sls` files are used to define instructions for all of your environments. It defines which states are applied to a salt-minion. 

It's important to note that it can follow a regex pattern or a node-group. This means that it's extremely important to name your salt-minions accordingly. `'*'` will apply states to all minions whereas `'dev*'` would only those states to salt-minions prefixed with a `dev` name. 

——————

I hope by this point you’ve also discovered Chef, Ansible, Puppet, and other similar offerings and you’re looking for ways to evaluate what makes the most sense for your company. SaltStack is a great tool but there are plenty of other tools that solve similar problems. Research each tool, find one that makes long-term sense and GO FOR IT!

SaltStack has done wonders for my organization. Prior to adopting this toolchain, our infrastructure was all over the place. Developers managed their own boxes. No environment shared any similarity. Knowledge of how to setup infrastructure was lost in half-finished documentation or internalized by senior developers. It’s safe to say we were all over the place without it. 

Adopting SaltStack took a lot of maturity and patience. You had to trust that building out the automation scripts will save you lots of time in the end in the long run. In the 1+ years since adopting it, we’ve had great success managing our infrastructure. DEV/TEST/STAGE/PROD are all similar minus environment configurations. VMs are stateless meaning I can tear down any of my AWS environments and have a fresh copy up within minutes. I’ve heard less “It works on my machine” issues.

Tune in to future posts where I’ll share some SaltStack best practices, automation scripts and creative ways to solve problems with SaltStack. 