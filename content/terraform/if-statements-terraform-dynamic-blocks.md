Title: If Statements Inside Terraform Dynamic Blocks 
Date: 2023-01-24
Modified: 2023-06-16
Tags: terraform, terragrunt, aws, amazon, dynamic, modules, django, python, cloud, if, if-statements, logic, if-logic, conditional, aws_lb_listener, resource
Slug: if-statements-terraform-dynamic-blocks
Author: Miguel Lopez
Summary: A guide to help you build if-statements inside Terraform dynamic blocks. By the end of this guide, you will understand how to create two **default_action** blocks for the **aws_lb_listener** resource.

Technical Stack: AWS, Terraform

Read: 5 minutes

## Introduction

[Dynamic Blocks](https://www.terraform.io/docs/language/expressions/dynamic-blocks.html) are used to create if statements inside Terraform resources. Dynamic blocks can be used with any **literal** block inside a Terraform resource.

For example, the `default_action` block inside the `aws_lb_listener` resource is a literal block.

```
resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.application.arn

  dynamic "default_action" {
    # but the "default_action" block is always a literal block
  }
}
```

After reading this, you will understand: 

- How to include multiple `default_action` blocks for the Terraform `aws_lb_listener` resource.
- How to make an optional `default_action` block.
- How to write an if-statement for `default_action` using a `dynamic` block.

## If Statements Inside Dynamic Blocks

You'll use a Terraform [dynamic block](https://www.terraform.io/docs/language/expressions/dynamic-blocks.html) to create the if-statement.

The basic setup looks like this:
```
dynamic "default_action" {
    for_each = var.default_action_type == "authenticate-oidc" ? [1] : []
    ...
}
```
 
In this example, we use the `for_each` combined with a [ternary operator](https://www.terraform.io/docs/language/expressions/conditionals.html#ternary-operator) to create the if-statement. If this logic statement is **true**, then [1] will be passed back and the block will be created.
 
Setting `var.default_action_type` to `null` or `forward` will not create the block.

## Using If Statements for aws_lb_listener

In this example, we will use the `dynamic` block to create an optional `default_action` block for the `aws_lb_listener` resource.

1. Start by looking at the example below
2. Notice the `dynamic "default_action" {}` blocks in the **aws_lb_listener** resource. These **two** dynamic blocks are used as "if" statements.
3. Set the `var.default_action_type` to select which "default_action" block to create.
   - `var.default_action_type == "forward"` will create the **forward** block.
   - `var.default_action_type == "authenticate-oidc"` will create the **authenticate-oidc** block. 


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

Think about using this strategy to create optional blocks when configuring you create a Terraform module that can be used in multiple places.

This load balancer module has been perfect for creating ALBs that are used by multiple types applications. Some of our applications are simple and only needed the `forward` action. While other applications were private needed the `authenticate-oidc` action.

All done for now. Hopefully that helps!

