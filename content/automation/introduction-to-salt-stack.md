Title: Introduction to SaltStack
Date: 2018-03-22
Modified: 2018-04-16
Tags: saltstack, aws, cloud
Slug: my-super-post
Author: Miguel Lopez
Summary: SaltStack 101, Set up your first Salt-Master and Salt-Minion


_Technical Environment: SaltStack v1.2123, AWS EC2 (CentOS ami)_

_Difficulty: Easy_

_Read: 25 minutes_

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

```
[root@salt-master salt]# service salt-master restart
```
Quickly restart the salt-master to load the new configurations. 

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

9. We are now ready to run our first state. Run the following `state.show_top` command to see which states will be applied.

```
[root@salt-master base]# salt '*' state.show_top
dev-minion-01:
    ----------
    base:
        - touch-file
```
_I always run `state.show_top` before running a `state.apply` to double check my salt-master is doing what I want. I can't stress this enough. It has saved me so many times._

10. If everything looks good, run the `state.apply` command to push the state down to the salt-minion.

```
[root@salt-master base]# salt '*' state.apply
dev-minion-01:
----------
          ID: /tmp/hello-world.txt
    Function: file.managed
      Result: True
     Comment: File /tmp/hello-world.txt updated
     Started: 06:17:46.887924
    Duration: 70.182 ms
     Changes:
              ----------
              diff:
                  New file
              mode:
                  0644

Summary for dev-minion-01
------------
Succeeded: 1 (changed=1)
Failed:    0
------------
Total states run:     1
Total run time:  70.182 ms
```

If everything went well, you should see `Succeeded: 1 (changed=1)`. This means that your state was successfully applied. You should now head back over to your salt-minion and verify that the state was successfully pushed. 

11. Verify `/tmp/hello-world.txt` exists on the salt-minion exists. 

```
[root@ip-10-0-1-97 ec2-user]# cat /tmp/hello-world.txt
hello world
```

There you have it, your first salt state!

## **Terraform**

In case you are familiar with Terraform, I've started to make some effort toward terraforming this whole process. Feel free to follow that progress on my [github](https://github.com/lopezm1/terraform-101/blob/master/mgmt/main.tf).

You can also find some salt-scripts that'll bootstrap autoscaling VMs as salt-minions [here](https://github.com/lopezm1/salt-scripts). 

## **Conclusion**

I've just scraped the surfrace with what you can do with Salt-Master. Over the next few weeks I'll be sure to add some more articles that will describe how to:

- configure different enviroments
- use pillars
- automatically push states to auto-scaling groups
- using salt formulas to create modular states

By this point, I hope you can understand how awesome Salt really is. SaltStack has been fantastic for our company and I hope it can do the same for you.

In case you are evaluating other tools, I recommend you check out [Chef](https://www.chef.io/chef/), [Ansible](https://www.ansible.com/) and [Puppet](https://puppet.com/) as they all have very similar functionality. 

It takes time and patience to fully adopt a configuration manager but the payoff is totally worth it. 