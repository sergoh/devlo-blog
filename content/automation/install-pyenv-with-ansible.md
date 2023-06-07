Title: Install Pyenv on Linux with Ansible
Date: 2023-06-06
Modified: 2023-06-06
Tags: packer, ansible, python, pyenv, devops, pyenvironment, automation, bash, images
Slug: install-pyenv-on-linux-with-ansible
Author: Miguel Lopez
Summary: Install Pyenv on Linux using an Ansible Galaxy Role. This is useful for managing Python versions on your local machine or on a target linux machine.

Technical Stack: Pyenv, Ansible, Linux

## Introduction

Pyenv is a tool for managing multiple versions of Python on your local machine. By the end of this turtorial, you will understand how you can use [staticdev/ansible-role-pyenv](https://github.com/staticdev/ansible-role-pyenv) Ansible role to manage your Pyenv installation.


### Install Ansible Role

You can add this role to the `requirements.yml` file in your Ansible project:

```yml
# requirements.yml
---
roles:
- name: staticdev.pyenv
```

Then run the following command to install the role:

```bash
ansible-galaxy install -r requirements.yml
```

### Use Ansible Role in Playbook

One option of using this role will be inside your `playbook.yml` file:

```yml
# playbook.yml
---
- hosts: servers
  roles:
    - role: staticdev.pyenv
      pyenv_env: "system"
      pyenv_global:
        - 3.11.0
        - 3.10.6
      pyenv_enable_autocompletion: false
      pyenv_python_versions:
        - 3.11.0
        - 3.10.6
```

### Import Role Inside Existing Tasks

You can also import the `staticdev.pyenv` role inside an existing playbook task like so:

```yml
- name: install pyenv
  import_role:
    name: staticdev.pyenv
  vars:
    pyenv_env: 'system'
    pyenv_global: ["3.8.16"]
    pyenv_python_versions: ["3.8.16"]
    pyenv_uninstall_python_w_wrong_configure_opts: False
```

### Full Configuration Options

For a full list of configuration options, please visit the github page for this role: [staticdev/ansible-role-pyenv](https://github.com/staticdev/ansible-role-pyenv#role-variables)


### Verify Pyenv Installation

After executing your ansible build, your target machine will have Pyenv installed. You can verify this by running the following command:

```bash
pyenv versions
```

### Using on CI/CD Pipeline

Be sure to increase the wait timeout of your CI/CD pipeline to allow for the installation of Pyenv. These builds can take up to 15 minutes to complete.

Something similar to `no_output_timeout: 30m` is good.
