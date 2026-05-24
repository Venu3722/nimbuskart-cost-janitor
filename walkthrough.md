# Cost Janitor – Complete Project Documentation

# Walkthrough Notes

## Project Introduction

This project simulates a cloud cost hygiene workflow using:

* Terraform
* LocalStack
* Python
* GitHub Actions

The goal is to identify orphaned or wasteful cloud resources and generate actionable cleanup reports.

The project demonstrates:

* Infrastructure as Code (IaC)
* cloud governance concepts
* automation workflows
* safe cleanup design
* CI/CD integration

The infrastructure is executed locally using LocalStack instead of a real AWS account.

---

# Why Cost Hygiene Matters

Unused cloud resources increase operational cost and reduce infrastructure visibility.

Examples:

* unattached EBS volumes
* stopped EC2 instances
* unused Elastic IPs
* improperly tagged resources

This project demonstrates how automation can help identify such resources before they become production-scale cost issues.

---

# High-Level Architecture

```text
Terraform
    ↓
LocalStack Infrastructure
    ↓
Python Cost Janitor Scan
    ↓
Generated Reports
    ↓
GitHub Actions Artifact Upload
```

---

# Technology Stack

| Component             | Purpose                     |
| --------------------- | --------------------------- |
| Terraform             | Infrastructure provisioning |
| LocalStack            | Local AWS simulation        |
| Python                | Cost hygiene automation     |
| boto3                 | AWS SDK for Python          |
| GitHub Actions        | CI/CD automation            |
| Markdown/JSON Reports | Reporting                   |

---

# Project Structure

```text
project-root/
│
├── terraform/
│   ├── modules/
│   │   └── network/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   │
│   ├── main.tf
│   ├── provider.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── janitor/
│   ├── janitor.py
│   └── requirements.txt
│
├── reports/
│   ├── report.json
│   └── report.md
│
├── .github/
│   └── workflows/
│       └── cost-janitor.yml
│
└── README.md
```

---

# Infrastructure Overview

Terraform provisions:

* VPC
* Public subnets
* Security group
* EC2 instances
* S3 bucket
* orphaned EBS volume
* unused Elastic IP

The infrastructure intentionally contains unused resources so the scanner can detect and report them.

---

# Terraform Structure

Key folders:

```text
terraform/
 ├── modules/network/
 ├── main.tf
 ├── provider.tf
 └── variables.tf
```

Networking resources were modularized to improve:

* maintainability
* readability
* scalability
* reusability

---

# Terraform Design Decisions

## LocalStack Endpoint Configuration

Terraform uses explicit LocalStack endpoints instead of real AWS services.

Example services:

* EC2
* S3
* IAM
* VPC

This enables:

* local testing
* zero cloud cost
* reproducible execution
* safer experimentation

---

## Terraform Local Wrapper Decision

Standard Terraform with explicit LocalStack endpoints was preferred over terraform-local for:

* portability
* Windows compatibility
* reduced wrapper dependency
* closer alignment with production Terraform workflows

---

# LocalStack Configuration

## LocalStack Version Pinning

Pinned version:

```text
localstack/localstack:3
```

Reason:
Newer LocalStack versions introduced authentication/licensing behavior that affected local reproducibility.

Version pinning ensures:

* predictable execution
* consistent demos
* stable CI/CD runs

---

# Cost Janitor Overview

The Python janitor scans LocalStack resources using boto3 APIs.

Primary responsibilities:

* detect orphaned resources
* identify unused infrastructure
* validate governance tags
* generate cleanup reports

Generated outputs:

* report.json
* report.md

---

# Current Detection Rules

## 1. Unattached EBS Volumes

Detects:

* EBS volumes not attached to EC2 instances

Why important:
Unused storage continues generating unnecessary cost.

---

## 2. Stopped EC2 Instances

Detects:

* EC2 instances in stopped state

Why important:
Stopped instances may still incur storage and infrastructure cost.

Safety note:
Stopped EC2 instances are intentionally excluded from automated deletion because they may represent temporary operational workloads.

---

## 3. Unused Elastic IPs

Detects:

* Elastic IP addresses not attached to instances

Why important:
Unused Elastic IPs may generate unnecessary charges.

---

## 4. Missing Required Tags

Detects missing governance tags such as:

* Owner
* Environment
* Project

Why important:
Proper tagging improves:

* cost tracking
* ownership visibility
* governance compliance

---

# Example Findings

Example scan results:

```text
- orphaned EBS volume: vol-12345
- stopped EC2 instance: i-12345
- unused Elastic IP
- S3 bucket missing Owner tag
```

---

# Safety Design

The scanner prioritizes safe automation.

## Dry-Run Mode

The scanner runs in dry-run mode by default.

Example:

```bash
python janitor/janitor.py
```

This generates reports without deleting resources.

---

## Explicit Delete Protection

Deletion requires explicit confirmation using:

```bash
python janitor/janitor.py --delete
```

This reduces accidental destructive operations.

---

## Protected Resource Handling

Resources tagged with:

```text
Protected=true
```

are skipped automatically.

This simulates production-grade protection controls.

---

# Generated Reports

## JSON Report

File:

```text
reports/report.json
```

Purpose:

* machine-readable output
* automation integration
* CI/CD compatibility

---

## Markdown Report

File:

```text
reports/report.md
```

Purpose:

* human-readable reporting
* easier review
* demo presentation

---

# CI/CD Workflow

GitHub Actions automates the complete workflow.

Workflow file:

```text
.github/workflows/cost-janitor.yml
```

---

# GitHub Actions Pipeline Flow

## Step 1 – Start LocalStack

Launch LocalStack container.

---

## Step 2 – Initialize Terraform

Run:

```bash
terraform init
```

---

## Step 3 – Apply Infrastructure

Run:

```bash
terraform apply -auto-approve
```

---

## Step 4 – Execute Cost Janitor

Run:

```bash
python janitor/janitor.py
```

---

## Step 5 – Upload Reports

Generated reports are uploaded as GitHub Actions artifacts.

---

# Demo Flow

## Step 1

Show Terraform infrastructure:

* VPC
* EC2
* EBS
* S3
* Elastic IP

Explain modular Terraform structure.

---

## Step 2

Run:

```bash
python janitor/janitor.py
```

Show detections:

* orphan EBS
* missing tags
* stopped EC2
* unused EIP

---

## Step 3

Open generated reports:

* report.json
* report.md

Explain:

* machine-readable reporting
* human-readable reporting

---

## Step 4

Show GitHub Actions workflow success:

* successful pipeline execution
* uploaded artifacts
* CI/CD automation flow

---

# Engineering Decisions

| Decision                   | Reason                          |
| -------------------------- | ------------------------------- |
| LocalStack instead of AWS  | Safe local testing              |
| Modular Terraform          | Better maintainability          |
| Dry-run by default         | Safer automation                |
| Explicit delete flag       | Prevent accidental cleanup      |
| Protected tags             | Simulated production safeguards |
| JSON + Markdown reports    | Machine + human readability     |
| GitHub Actions integration | CI/CD automation                |

---

# Known Limitations

## S3 Lifecycle Configuration

Lifecycle configuration was excluded from active LocalStack execution because LocalStack lifecycle APIs caused repeated timeout behavior.

---

## Limited Cloud Coverage

The current implementation focuses on a subset of AWS resources.

Future versions may expand support for:

* RDS
* Load Balancers
* NAT Gateways
* EKS resources
* Lambda functions

---

# Future Enhancements

Potential improvements:

* Slack/MS Teams notifications
* automated cleanup approvals
* HTML dashboard reporting
* policy-as-code integration
* scheduled scans
* multi-account support
* historical trend tracking
* cost estimation integration

---

# Learning Outcomes

This project demonstrates practical experience with:

* Terraform Infrastructure as Code
* LocalStack cloud simulation
* Python automation scripting
* boto3 SDK usage
* GitHub Actions CI/CD
* cloud governance concepts
* cost optimization workflows
* modular infrastructure design
* safe automation engineering

---

# Key Takeaways

This project demonstrates:

* Infrastructure as Code using Terraform
* Local AWS simulation with LocalStack
* Python automation using boto3
* CI/CD automation with GitHub Actions
* safe cleanup workflow design
* modular infrastructure organization
* cloud governance principles
* cost optimization strategies

---

# Final Notes

The project prioritizes:

* reproducibility
* safety
* modularity
* maintainability
* realistic cloud automation workflows

rather than large-scale enterprise complexity.

It serves as a practical demonstration of modern DevOps and SRE engineering practices using fully local cloud simulation.
