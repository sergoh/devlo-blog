Title: for_each Loops w/ If Statements in Terraform 0.12.6+
Date: 2021-12-01
Modified: 2021-12-01
Tags: terraform, logic, aws, if, loop, for-each
Slug: terraform-for-each-if-statement
Author: Miguel Lopez
Summary: Real life example that demonstrates how to use for_each loops with an if conditional that determines if the resource is built or not. 

Technical Stack: Terraform 0.12.6+
Read: 5 minutes

## **Prerequisites**

- Terraform

These days, I recommend installing terraform with `tfenv` and managing everything through there.

For mac users: `brew install tfenv && tfenv install latest`

## **Introduction**

This tutorial will help you build Terraform resources in a `for_each` loop with an `if` statement conditional. That `if` conditional will determine if `resource` 
is built or not.

## **Building the For-Each Loop**

Starting in Terraform `0.12.6+` the `for_each` loop was supported for all `resource` and `module` blocks in Terraform.

This was an incredibly powerful feature that enabled us to build complex `any` blocks as inputs. You could define modules
that had the same infrastructure goals but slightly different resources. 

--- 
### Background

Imagine you're building a microservice with API and worker services. Each service component will require an autoscaling group. 
However, **not** every autoscaling group requires a load balancer. 

How can we build a module that does not require a load balancer for each service component being defined?

Take the following input as an example:
```yml
services:
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
```
_(represented as [ymlencoded input](https://www.terraform.io/language/functions/yamldecode), check out documentation for details)_

### Building the Loop

For this example, the `if` statement lives inside the `for_each` loop. Notice how I use `{ }` around my loop. This tells 
Terraform we are reducing our complex `var.services` object based on the `if` result.

`for_each = { for key, value in var.services : key => value if value.load_balancer_enabled == true }`

The most important bit of this line is `if value.load_balancer_enabled == true`. If you take a look at my input above, 
you'll notice that the `worker` has `load_balancer_enabled: false`. This will result in the `if` statement in our `for_each`
loop removing the `worker` object from the loop. 

Now only services that require will build out the load balancers they need. 

This is an extremely useful trick for building dynamic modules with configurable resources.

Here is the full example on `load_balancer` module:
```terraform
module "load_balancer" {
  for_each  = { for key, value in var.services : key => value if value.load_balancer_enabled == true }
  source    = "../load-balancer"  # custom module reference as an example

  name                       = "${each.key}"
  enable_deletion_protection = lookup(each.value.load_balancer, "enable_deletion_protection", true)

  domain             = lookup(each.value.load_balancer, "domain", null)
  security_groups    = lookup(each.value.load_balancer, "security_groups", [])
  internal           = lookup(each.value.load_balancer, "internal", true)
  load_balancer_type = lookup(each.value.load_balancer, "load_balancer_type", "application")

  tags = merge(jsondecode(var.tags), lookup(each.value, "tags", {}), local.common_tags)

  target_groups        = { for key, value in lookup(each.value.load_balancer, "target_groups", {}) : key => merge(value, { target_group_name = format("%s-%s-%s", each.key, key, var.color) }) }
  load_balancer_listeners         = lookup(each.value.load_balancer, "listeners", {})
  extra_listener_rules = lookup(each.value.load_balancer, "extra_listener_rules", {})
  extra_ssl_certs      = lookup(each.value.load_balancer, "extra_ssl_certs", {})
}
```

### Additional Example

The example above consumed a `load_balancer` module in order to build the load balancer required by each service. 

In case you wanted to see this `for_each` loop on a `resource`, I also included that. 

In this example, we'll be using a complex variable called `extra_load_balancer` to define array of objects that create 
Terraform load balancers. Network load balancers will always require a VPC link in this scenario. 

Inputs: 
```yml
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
```

Building the loop:
```terraform
resource "aws_api_gateway_vpc_link" "link" {
  for_each    = { for key, value in var.extra_load_balancers : key => value if lookup(value, "load_balancer_type", "application") == "network" }
  name        = format("%s-%s", each.key)
  target_arns = [module.extra_load_balancer[each.key].lb_arn]

  depends_on = [module.extra_load_balancer.lb_arn]
}
```

## **Conclusion**

Hope this helps!

-- Miguel Lopez