Title: If Statements Inside Terraform Dynamic Blocks 
Date: 2023-01-24
Modified: 2023-01-24
Tags: local, terraform, terragrunt, aws, amazon, dynamic, modules, django, python, cloud, eventbridge, sns, s3, sqs, if, if-statements, logic, if-logic, conditional, aws_lb_listener, resource
Slug: if-statements-terraform-dynamic-blocks
Author: Miguel Lopez
Summary: Learn how to use if-statements inside Terraform Dynamic blocks.

Technical Stack: AWS, Terraform

Read: 5 minutes

## Introduction

The `default_action` for the Terraform `aws_lb_listener` resource is known as a Terraform configuration block. Configuration blocks can be wrapped in a `dynamic` block to conditionally include different configurations blocks for a resource.

[More Info on Dynamic Blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks).

After reading this, you will understand: 

- How to include multiple `default_action` blocks for the Terraform `aws_lb_listener` resource.
- How to make an optional `default_action` block.
- How to write an if-statement for `default_action` using a `dynamic` block.

## If Statements Inside Dynamic Blocks

Creating an if-statement inside a `dynamic` block is pretty simple.

The basic setup looks like this:
```
dynamic "default_action" {
    for_each = var.default_action_type == "authenticate-oidc" ? [1] : []
    ...
}
```
 You'll use the `for_each` loop to create the `dynamic "default_action" {}` when the `var.default_action_type == "authenticate-oidc"`.
 
 This example returns `[1]` when the conditional if-statement is **true**.
 
 The `[1]` passed back to the `for_each` means the `dynamic "default_action"` will be created.

## Real Terraform Examples

Here's how to use these if-statements in a real Terraform file..

1. Notice the **two** conditionals if-statements for the two different `dynamic "default_action" {}` blocks in the `aws_lb_listener` resource. 
2. The `default_action` is selected by a matching the `var.default_action_type` to `dynamic` block.
3. Use `var.target_group_arn` for `var.default_action_type == "forward"` to include the target group.
4. Use `varauthenticate_oidc` for `var.default_action_type == "authenticate-oidc"` to include oidc configuration.

**resources.tf**
```terraform
resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.application.arn

  port     = var.port
  protocol = var.protocol

  # Allow Forward Action
  dynamic "default_action" {
    for_each = var.default_action_type == "forward" ? [1] : []
    content {
      type = "forward"
      forward {
        target_group_arn                    = var.target_group_arn
      }
    }
  }

  # Allow Authenticate-OIDC Action
  dynamic "default_action" {
    for_each = var.default_action_type == "authenticate-oidc" ? [1] : []
    content {
      type = "authenticate-oidc"
      authenticate_oidc {
        authorization_endpoint              = lookup(var.authenticate_oidc, "authorization_endpoint")
        client_id                           = lookup(var.authenticate_oidc, "client_id")
        client_secret                       = lookup(var.authenticate_oidc, "client_secret")
        issuer                              = lookup(var.authenticate_oidc, "issuer")
        token_endpoint                      = lookup(var.authenticate_oidc, "token_endpoint")
        user_info_endpoint                  = lookup(var.authenticate_oidc, "user_info_endpoint")
        scope                               = lookup(var.authenticate_oidc, "scope", null)
        session_timeout                     = lookup(var.authenticate_oidc, "session_timeout", 2628000)
        authentication_request_extra_params = lookup(var.authenticate_oidc, "authentication_request_extra_params", null)
      }
    }
  }
```

**variables.tf**
```
variable "port" {
  default = 80
  type    = number
}

variable "protocol" {
  default = "HTTP"
  type    = string
}

variable "default_action_type" {
  description = "Type of Default Action"
}

variable "authenticate_oidc" {
  default = null
  type    = map(any)
}

variable "target_group_arn" {
  default = null
  type    = string
}
```

## Conclusion

All done for now. Hopefully that helps!

-----------

**Terraform** is an Infrastructure-as-Code tool that enables to you safely manage and deploy infastructure on multiple cloud providers. 

[Read More About Terraform](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
