Title: If, If-else Statements in Terraform
Date: 2018-04-10
Modified: 2018-04-10
Tags: aws, cloud, terraform, hcl, hashicorp
Slug: if-else-terraform
Author: Miguel Lopez
Summary: Using if-else statements in terraforms


_Terraform v0.11.5_

## **Introduction**

In HCL, a boolean is one of the many ways you can create an if-statement.

Booleans can be used in a Terraform tenerary operation to create an if-else statement. Ternary operations follow the syntax: 

```
CONDITION ? TRUEVAL : FALSEVAL
```

Combine this idea with a boolean conditional and you have an if statement. A boolean ternary function would look like....

```
${var.create_eip == true ? 1 : 0}
```
If the variable `create_ip` == `true` then return 1, else return 0. We will combine this idea with the `count` attribtue of a resource to create an if-else statement. 

## **If Statement**

Start by looking at the boolean value we are passing to `create_eip` in this module. 

```hcl-terraform
module "frontend" {
  source = "/modules/frontend-app"
  box_name = "web-01"
  ami = "ami-25615740"
  instance_type = "t2.micro"
  create_eip = true
}
```
Based on HCL semantics, setting the `create_eip` to `true` would result in the ternary operation `${var.create_eip == true ? 1 : 0}` resolving to value of 1.
This means a value of 1 would be passed on to the `count` parameter of the `aws_eip` resource. This would create one eip resource.

```hcl-terraform
# frontend-app module
variable "create_eip" {
  description = "Create an EIP if set to True"
}

resource "aws_eip" "web-eip" {
  count = "${var.create_eip == true ? 1 : 0}"
  instance = "${aws_instance.example.id}"
}
```

## **If-Else Statement**
 
Create an if-else statement in a similar manner.

Take a careful look at the following `if-eip`, `else-eip` example. We will use two tenary operations to achieve if-else.

```hcl-terraform
module "frontend" {
  source = "/modules/frontend-app"
  box_name = "web-01"
  ami = "ami-25615740"
  instance_type = "t2.micro"
  create_first_eip = true
}
```
```
# frontend-app module
variable "create_first_eip" {
  description = "Create the first eip if set to true, otherwise create the second eip if set to false"
}

resource "aws_eip" "if-eip" {
  count = "${var.create_first_eip == true ? 1 : 0}"
  instance = "${aws_instance.example.id}"
}

resource "aws_eip" "else-eip" {
  count = "${var.create_first_eip == false ? 1 : 0}"
  instance = "${aws_instance.example.id}"
}
```

If the `create_first_eip` variable was set to `true` then the first `aws_eip` would be created because the `create_first_eip == true` would result in a `count` of 1.

If the `create_first_eip` variable was set to `false`, then the second `aws_eip` would be created because the `create_first_eip == false` would result in a `count` of 1. The first `aws_eip` would not be created because it would fail the conditional statement. 

This creates an if-else pattern. 