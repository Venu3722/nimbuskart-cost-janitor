# Walkthrough Notes

## Project Introduction

This project simulates a cloud cost hygiene workflow using:
- Terraform
- LocalStack
- Python
- GitHub Actions

The goal is to identify orphaned or wasteful cloud resources and generate actionable cleanup reports.

---

# Infrastructure Overview

Terraform provisions:
- VPC
- public subnets
- security group
- EC2 instances
- S3 bucket
- orphaned EBS volume
- unused Elastic IP

The infrastructure runs locally on LocalStack instead of real AWS.

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

Networking resources were modularized to improve maintainability.

---

# Cost Janitor Overview

The Python janitor scans LocalStack resources using boto3.

Current detections:
- unattached EBS volumes
- stopped EC2 instances
- unused Elastic IPs
- missing required tags

Generated outputs:
- report.json
- report.md

---

# Safety Design

The scanner:
- runs in dry-run mode by default
- requires explicit `--delete`
- skips resources tagged with `Protected=true`

Stopped EC2 instances are intentionally marked unsafe for automatic deletion.

---

# CI/CD Workflow

GitHub Actions:
1. Starts LocalStack
2. Runs Terraform
3. Executes Cost Janitor
4. Uploads generated reports

Workflow file:

```text
.github/workflows/cost-janitor.yml
```

---

# Engineering Decisions

## LocalStack Version Pinning

Pinned:

```text
localstack/localstack:3
```

due to authentication/licensing behavior observed in newer releases.

---

## Terraform Local Wrapper

Standard Terraform with explicit LocalStack endpoints was preferred over terraform-local for portability and Windows compatibility.

---

## S3 Lifecycle Configuration

Lifecycle configuration was excluded from active LocalStack execution because LocalStack lifecycle APIs caused repeated timeout behavior.

---

# Demo Flow

## Step 1
Show Terraform infrastructure.

---

## Step 2
Run:

```bash
python janitor/janitor.py
```

Show:
- orphan EBS
- missing tags
- stopped EC2
- unused EIP

---

## Step 3
Open generated:
- report.json
- report.md

---

## Step 4
Show GitHub Actions workflow success.

---

# Final Notes

The project prioritizes:
- reproducibility
- safety
- modularity
- realistic cloud automation workflows

rather than large-scale enterprise complexity.