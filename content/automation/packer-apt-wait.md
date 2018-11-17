Title: Building Robust Packer AMIs
Date: 2018-11-16
Modified: 2018-11-16
Tags: aws, cloud, EC2, automation, packer, apt, apt-get, ub ubutnu
Slug: packer-ami-apt-get
Author: Miguel Lopez
Summary: How to avoid `Could not get lock /var/lib/dpkg/lock` while using Packer


Technical Stack: AWS EC2 (AWS AMI CentOS), Packer, Ubuntu 18.04
Read: 10 minutes 

## **Introduction**

Hey everyone! Sorry for the absence. I started a new job in San Francisco that attracted my attetnion the past few months.

I wanted to write a quick post about an issue I encounted while creating AWS AMIs using Packer, EC2, and Ubuntu 18.04. 

For those of you who don't know, [Packer]() is an automation tool you can use to prepack AMIs with custom libraries or dependency your code may need upon launching. You can choose to run multiple provisioners (scripts, chef, ansible, etc) against an a base AMI in order to create your image. 

## **Race conditions w/ apt-get update**

The first issue I encountered while using Packer was while I ran `sudo apt-get update`. No matter how many times I ran it, I would consistently get:

```bash 
    AWS AMI Builder - CIS: Reading package lists...
    AWS AMI Builder - CIS: W: Target Packages (main/binary-amd64/Packages) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: W: Target Packages (main/binary-all/Packages) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: W: Target Translations (main/i18n/Translation-en) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: W: Target CNF (main/cnf/Commands-amd64) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: W: Target CNF (main/cnf/Commands-all) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: Installing unzip.....
    AWS AMI Builder - CIS: W: Target Packages (main/binary-amd64/Packages) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: W: Target Packages (main/binary-all/Packages) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: W: Target Translations (main/i18n/Translation-en) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: W: Target CNF (main/cnf/Commands-amd64) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: W: Target CNF (main/cnf/Commands-all) is configured multiple times in /etc/apt/sources.list.d/microsoft-prod.list:1 and /etc/apt/sources.list.d/microsoft.list:1
    AWS AMI Builder - CIS: /tmp/script_4426.sh: 6: /tmp/script_4426.sh: [[: not found
    AWS AMI Builder - CIS: E: Could not get lock /var/lib/dpkg/lock - open (11: Resource temporarily unavailable)
    AWS AMI Builder - CIS: E: Unable to lock the administration directory (/var/lib/dpkg/), is another process using it?
```

I did not understand why my simple script was causing `CIS: E: Could not get lock /var/lib/dpkg/lock` to occur. 

Here was my provisioner: 

```bash
"provisioners": [
    {
      "type": "shell",
      "inline": [
        "sudo apt-get update -y",
        "echo \"Installing unzip.....\"",
        "sudo apt-get --assume-yes install unzip",
        "echo \"Installing python.....\"",
        "sudo apt-get --assume-yes install python",
      ]
    }
  ]
```

It seemed like every other run would fail with a `CIS: E: Could not get lock /var/lib/dpkg/lock` error and I couldn't find a good solution. Further research proved that this error occurs whenever another process had a lock on the following file. It could be _any_ process using `apt`. 

I searched the internet and could only fine people that would suggest `pkill` on any process using apt found in `ps aux`. Or they would suggest `rm /var/lib/dpkg/lock`. Or would suggest `sleep 100` to give whatever process was using `apt` enough time to release it's lock. 

All seemed like terrible solutions to me and nothing seemed very robust. 


## **My Solution**

I wanted to be a solution that would listen to the processes and would not continue until the process using `apt` finishes. Whatever was using `apt` is probably doing it in a meaninful way so it's best to let it finish before moving on. 

My solution was simple. By using `ps aux` and some pipeing, we could listen to processes and only continue whenever apt was not being used by any other process.

```
wait_apt=$(ps aux | grep apt | wc -l)
while [ "$wait_apt" -gt "1" ]; do echo "waiting for apt-update...."; wait_apt=$(ps aux | grep apt | wc -l); sleep 5; done
```

To break this down... `ps aux` shows you a list of active processes, `grep apt` filters all processes to only include `apt` related ones and `wc -l` gives you a line count on your results. So effectively, this little command will show you a `2` or more whenever a process is using apt and a `1` if apt is unused. 

Combine that with a while loop and you have a pretty robust way of checking for an idle apt. 

Here was my complete provisioner afterwards:

```bash
  "provisioners": [
    {
      "type": "shell",
      "inline": [
        "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done",
        "wait_apt=$(ps aux | grep apt | wc -l)",
        "while [ \"$wait_apt\" -gt \"1\" ]; do echo \"waiting for apt to be ready....\"; wait_apt=$(ps aux | grep apt | wc -l); sleep 5; done",
        "sudo apt-get update -y",
        "wait_apt=$(ps aux | grep apt | wc -l)",
        "while [ \"$wait_apt\" -gt \"1\" ]; do echo \"waiting for apt-update....\"; wait_apt=$(ps aux | grep apt | wc -l); sleep 5; done",
        "echo \"Installing unzip.....\"",
        "sudo apt-get --assume-yes install unzip",
        "echo \"Installing python.....\"",
        "sudo apt-get --assume-yes install python",
      ]
    }
```
Finding this solution was important to me because I wanted to Packer to work 100% of the time. I didn't want to randomly encounter `CIS: E: Could not get lock /var/lib/dpkg/lock` errors. 