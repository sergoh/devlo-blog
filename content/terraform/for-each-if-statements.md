Title: Terraform for_each Loops w/ If Statements
Date: 2021-12-01
Modified: 2023-06-20
Tags: terraform, terragrunt, logic, aws, if, conditional, for-each, for-loop, loops
Slug: for-each-if-statements
Author: Miguel Lopez
Summary: A guide to help you build if statements inside Terraform for_each loops. This guide includes a few examples of how to use conditional logic inside Terraform for_each loops to control which resources are built.

Technical Stack: Terraform 0.12.6+, AWS

Read: 5 minutes

## Introduction

The most basic example of a **for_each** loop looks like this:

```
resource "s3_bucket" "rg" {
  for_each = {
    a_group = "bucket-1"
    b_group = "bucket-2"
  }
  name     = each.value
  tags = {
    Name = each.value
    Group = each.key
  }
}
```

Starting in **Terraform v0.12.6+**, the `for_each` loop became available for all Terraform resources and modules.

Building conditiional statements inside **for_each** is a powerful way to control which resources are built inside complex modules. For example, you can use a for_each loop to build an autoscaling group module that only builds a load balancer if the user specifies it. This is a great way to build dynamic and reusable modules.

[Full For-Each Documentation](https://www.terraform.io/docs/language/meta-arguments/for_each.html)


## Building Conditional If Statements

In this example, we're building a Load Balancer module that can be used to create multiple load balancers. If the user specifies a network load balancer, we'll build a VPC link to connect the load balancer to an API Gateway.

---

Let's imagine the **resource** block for the VPC link looks like this:

```terraform
resource "aws_api_gateway_vpc_link" "link" {
    for_each    = { for key, value in var.load_balancers : key => value if value.load_balancer_type == "network" }
    name        = each.key
    target_arns = [aws_target_group.lb[each.key].arn]
}
```

---

And given this input:

```yaml
load_balancers:
  application_lb:
    load_balancer_type: application
    security_groups: [ ]
    target_groups:
        <ommitted for simplicity>
  network_lb:
    load_balancer_type: network
    security_groups: [ ]
    target_groups:
        <ommitted for simplicity>
```

---

You can break down the **for_each** loop inside **aws_api_gateway_vpc_link** like this:

1. Loop through each key/value in `load_balancers`. Treat the `each.value` value as an object.
2. Check if the `each.value` contains `load_balancer_type = "network"`. 
3. If the `load_balancer_type` is `network`, then build the VPC link.



## Autoscaling Group Module Example

Imagine you're building a microservice with API and worker profiles. Each service component will require an autoscaling group. However, **not** every autoscaling group requires a load balancer.

How can we build a module that does not require a load balancer for each service component being defined?

----

You could build a **for_each** loop something like this:
```terraform
for_each = { for key, value in var.services : key => value if value.load_balancer_enabled == true }
```

---

Let's imagine our module looks like this:

```terraform
    module "load_balancer" {
      for_each  = { for key, value in var.services : key => value if lookup(value, "load_balancer_enabled", false) == true }
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
```

---

And given this input:

```yaml
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
```

Here's how to break down this **for_each** loop:

1. The `if` statement inside the **for_each** uses the `value.load_balancer_enabled` to check if the service requires a load balancer. Use `lookup()` to safely fetch the key from the object.
2. The `{ }` wrapped around my loop tells Terraform to reduce the `var.services` object based on the `if` statement result.
3. Build this resource/module for any object that contains `load_balancer_enabled = true`. In this example, only the **api** object will build a load balancer.
