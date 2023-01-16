:title: Terraform for_each loops w/ if statements in Terraform 0.12.6+
:date: 2021-12-01
:modified: 2021-12-01
:tags: terraform, terraform, logic, aws, if, loop, for-each, for-loop, loops
:category: terraform
:slug: for-each-if-statements
:authors: Miguel Lopez
:summary: Real life example that demonstrates how to use for_each loops with an if conditional that determines if the resource is built or not.


Technical Stack: Terraform 0.12.6+

Read: 5 minutes

Prerequisites
=============

- Terraform

These days, I recommend installing terraform with :code:`tfenv` and managing everything through there.

For mac users: :code:`brew install tfenv && tfenv install latest`

Introduction
============

This tutorial will help you build Terraform resources in a :code:`for_each` loop with an :code:`if` statement conditional.
That :code:`if` conditional will determine if :code:`resource` is built or not.


Building the For-Each Loop
==========================

Starting in :code:`Terraform 0.12.6+` the :code:`for_each` loop was supported for all :code:`resource` and :code:`module` blocks in Terraform.

This was an incredibly powerful feature that enabled us to build complex `any` blocks as inputs. You could define modules
that had the same infrastructure goals but slightly different resources.

Background
----------

Imagine you're building a microservice with API and worker services. Each service component will require an autoscaling group.
However, **not** every autoscaling group requires a load balancer.

How can we build a module that does not require a load balancer for each service component being defined?

Take the following input as an example:

.. code-block:: yaml

    services
      api:
        instance_type: t4g.medium
        min_size: 1
        max_size: 1
        desired_size: 1
        load_balancer_enabled: true
        load_balancer:
          internal: true
          <ommitted for simplicity>
      worker:
        instance_type: t4g.medium
        min_size: 1
        max_size: 1
        desired_size: 1
        load_balancer_enabled: false

`terraform input represented as ymlencoded input <https://www.terraform.io/language/functions/yamldecode>`_

Building the for_each loop
--------------------------

.. code-block:: terraform

    for_each = { for key, value in var.services : key => value if value.load_balancer_enabled == true }


In this example, the :code:`if` statement lives inside the :code:`for_each` loop. Notice how I use :code:`{ }` around my loop. This tells
Terraform we are reducing our complex `var.services` object based on the :code:`if` result.

The most important bit of this line is :code:`if value.load_balancer_enabled == true`. If you take a look at my input above,
you'll notice that the :code:`worker` has :code:`load_balancer_enabled: false`. This will result in the :code:`if` statement in our :code:`for_each`
loop removing the :code:`worker` object from the loop.

Now only services that require will build out the load balancers they need.

This is an extremely useful trick for building dynamic modules with configurable resources.

Here is the full example on :code:`load_balancer` module:

.. code-block:: terraform

    module "load_balancer" {
      for_each  = { for key, value in var.services : key => value if value.load_balancer_enabled == true }
      source    = "../load-balancer"  # custom module reference as an example

      name                       = each.key
      enable_deletion_protection = lookup(each.value.load_balancer, "enable_deletion_protection", true)

      domain             = lookup(each.value.load_balancer, "domain", null)
      security_groups    = lookup(each.value.load_balancer, "security_groups", [])
      internal           = lookup(each.value.load_balancer, "internal", true)
      load_balancer_type = lookup(each.value.load_balancer, "load_balancer_type", "application")

      tags = merge(jsondecode(var.tags), lookup(each.value, "tags", {}), local.common_tags)

      target_groups        = lookup(each.value.load_balancer, "target_groups", {})
      load_balancer_listeners         = lookup(each.value.load_balancer, "listeners", {})
      extra_listener_rules = lookup(each.value.load_balancer, "extra_listener_rules", {})
      extra_ssl_certs      = lookup(each.value.load_balancer, "extra_ssl_certs", {})
    }

Additional Example
==================

The example above consumed a :code:`load_balancer` module in order to build the load balancer required by each service.

In case you wanted to see this :code:`for_each` loop on a :code:`resource`, I also included that.

In this example, we'll be using a complex variable called :code:`extra_load_balancer` to define array of objects that create
Terraform load balancers. Network load balancers will always require a VPC link in this scenario.

Inputs
-------

.. code-block:: yaml

    extra_load_balancers:
      balancer_1:
        load_balancer_type: application
        enable_deletion_protection: false
        security_groups: [ ]
        target_groups:
          <ommitted for simplicity>
      balancer_2:
        load_balancer_type: network
        enable_deletion_protection: false
        security_groups: [ ]
        target_groups:
          <ommitted for simplicity>

Looping through a Resource
--------------------------

.. code-block:: terraform

    resource "aws_api_gateway_vpc_link" "link" {
      for_each    = { for key, value in var.extra_load_balancers : key => value if lookup(value, "load_balancer_type", "application") == "network" }
      name        = format("%s-%s", each.key)
      target_arns = [module.extra_load_balancer[each.key].lb_arn]

      depends_on = [module.extra_load_balancer.lb_arn]
    }


Conclusion
==========

Hope this helps!

-- Miguel Lopez