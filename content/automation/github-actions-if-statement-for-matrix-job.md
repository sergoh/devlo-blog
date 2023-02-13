Title: Github Actions: If Statement for Matrix Value
Date: 2023-02-11
Modified: 2023-02-11
Tags: github, actions, github-actions, devops, automation, matrix, job, if, if-statement 
Slug: github-actions-if-statement-matrix-value
Author: Miguel Lopez
Summary: Github Actions: Use an if statement to conditionally run a block given a specific matrix value. (Matrix Strategy Jobs)

Technical Stack: Github Actions

Read: 2 minutes

## Prerequisites 

- Github
- Github Actions

## Introduction

**Github Actions** is a continuous integration and continuous delivery (CI/CD) platform that allows you to automate your build, test, and deployment pipeline. [Read More Here.](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions)

**Matrix Jobs** lets you use variables in a single job definition to automatically create multiple job runs that are based on the combinations of the variables. For example, you can use a matrix strategy to test your code in multiple versions of a language or on multiple operating systems. [Source](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)

### After reading this, your will understand: 

- How Matrix Jobs run in Github Actions
- How to conditionally run a block given a specific matrix value

## Given This Matrix Strategy..

Github Actions allows you to pass an array of objects to define matrix jobs. This allows you to access the variables
at `matrix.platforms.os` or `matrix.platforms.os_version`.

```
jobs:
  create-image:
    name: 'Create Base Images'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        platforms: [ 
          { os: "ubuntu", os_version: "16.04", npm_version: 12, ruby: true }, 
          { os: "ubuntu", os_version: "18.04", npm_version: 16 }, 
          { os: "ubuntu", os_version: "20.04", npm_version: 16 }
        ]
```

## If Statement - Matrix Value Null / Boolean Check

For null/boolean comparisons, do not compare your matrix value to any strings, numbers or booleans. Use the format `if: matrix.platforms.ruby` for two reasons:

1. This format performs a *null* check on the `ruby` value. Jobs could choose to omit the `matrix.platforms.ruby` and this job will be skipped.
2. This format also peforms a *boolean* check if `ruby` contains a boolean value. 

```
- if: matrix.platforms.ruby
  name: Add Ruby Dependencies
  run: echo "Install Ruby specific packages."
```

[Full List of Github Action Operators](https://docs.github.com/en/actions/learn-github-actions/expressions#operators)

## If Statement - Matrix Value String / Number Comparison

For string values, be sure to enclose your value in single quotes `' '`. Enclosing them in double quotes `"` will throw an error. 

```
- if: matrix.platforms.os_version == '16.04'
  name: Add Ubuntu Packages (legacy)
  run: echo "Install Ubuntu 16.04 specific packages."
- if: matrix.platforms.npm_version == 16
  name: Add NPM Dependencies
  run: echo "Install NPM dependencies."
```

[Full List of Github Action Operators](https://docs.github.com/en/actions/learn-github-actions/expressions#operators)

## Full Github Action

```
name: 'Create Artifacts'
on:
  pull_request:
jobs:
  create-images:
    name: 'Create Base Images'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        platforms: [ 
          {os: "ubuntu", os_version: "16.04", legacy: true}, 
          {os: "ubuntu", os_version: "18.04"}, 
          {os: "ubuntu", os_version: "20.04"}
        ]
    steps:
      - if: matrix.platforms.os_version == '16.04'
        name: Add Ubuntu Packages (legacy)
        run: echo "Install Ubuntu 16.04 specific packages."
      - name: Add Ubuntu Packages
        run: echo "Install Ubuntu packages."
```

## Using A Different Matrix Strategy

Traditional Matrix Jobs are setup like this: 

```
jobs:
  example_matrix:
    strategy:
      matrix:
        os_version: ['16.04', '18.04', '20.04']
        os: ['ubuntu']
```

You could still use if statements in the following way:

```
if: matrix.os_version == '18.04'
```

### Includes and Excludes

Github Actions has support to skip an entire matrix value using `include` or `exclude`. The following configuraiton
would skip the `{ "os": "ubuntu", "os_version": "16.04" }` job. 

```
exclude:
    - os_version: '16.04'
```

Using `exclude` or `include` skips the entire workflow. *For this reason, it's sometimes better to use `if` statements in order to accomplish your workflow.*
