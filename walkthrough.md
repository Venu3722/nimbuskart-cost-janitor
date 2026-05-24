# Cost Janitor – Cloud Cost Hygiene Simulation Project

## Project Overview
**Cost Janitor** is a lightweight cloud cost hygiene simulation project designed to identify unused, orphaned, or improperly tagged cloud resources. The project demonstrates practical DevOps and SRE concepts using:
* Terraform
* LocalStack
* Python
* GitHub Actions

Instead of provisioning infrastructure in a real AWS account, the project uses LocalStack to simulate AWS services locally and safely.

### Primary Goals
* Showcase Infrastructure as Code (IaC) principles.
* Demonstrate cloud governance and automation workflows.
* Implement cost optimization strategies.
* Integrate CI/CD security and compliance checks.
* Practice safe cleanup design patterns.

---

## Why Cost Hygiene Matters
Cloud environments often accumulate unused or forgotten resources over time. Examples include:
* Unattached storage volumes
* Stopped virtual machines
* Unused public IPs
* Improperly tagged resources

These resources increase operational cost, reduce visibility, and create governance challenges. This project demonstrates how automated scanning workflows can help identify such issues before they become production-scale problems.

---

## Technology Stack


| Component | Purpose |
| :--- | :--- |
| **Terraform** | Infrastructure provisioning |
| **LocalStack** | Local AWS cloud simulation |
| **Python** | Cost hygiene scanning logic |
| **Boto3** | AWS SDK for Python |
| **GitHub Actions** | CI/CD automation |
| **Markdown/JSON** | Scan reporting |

---

## High-Level Architecture


Terraform
    ↓
LocalStack Infrastructure
    ↓
Python Cost Janitor Scan
    ↓
Generated Reports
    ↓
GitHub Actions Artifact Upload

## Project Structure

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

**Infrastructure Overview**

Terraform provisions the following simulated AWS resources inside LocalStack:

Resource	Purpose
VPC	Network isolation
Public Subnets	Infrastructure networking
Security Group	Access control
EC2 Instances	Simulated compute workloads
S3 Bucket	Object storage
Orphaned EBS Volume	Cost hygiene detection example
Unused Elastic IP	Cost hygiene detection example

The infrastructure is intentionally designed to include some wasteful resources so the Cost Janitor scanner can identify them.

Terraform Design
Modular Structure

Networking resources were separated into reusable modules for better maintainability and scalability.

Example:

terraform/modules/network/

Benefits:

cleaner organization
easier reuse
improved readability
scalable infrastructure structure
Provider Configuration

Terraform uses LocalStack endpoints instead of real AWS services.

Example services:

EC2
S3
VPC
IAM

This allows fully local infrastructure testing without cloud cost exposure.

LocalStack Configuration
LocalStack Version Pinning

Pinned version:

localstack/localstack:3

Reason:
Newer LocalStack versions introduced authentication/licensing behavior that affected local reproducibility.

Version pinning ensures:

predictable execution
consistent demos
stable CI/CD runs
Terraform Local Wrapper Decision

The project intentionally uses standard Terraform with explicit LocalStack endpoints instead of terraform-local.

Reason:

better portability
improved Windows compatibility
fewer wrapper dependencies
closer alignment with real Terraform workflows
Cost Janitor Scanner
Scanner Overview

The Python-based Cost Janitor scans LocalStack resources using boto3 APIs.

Main responsibilities:

detect orphaned resources
identify unused infrastructure
validate governance tags
generate actionable reports
Current Detection Rules
1. Unattached EBS Volumes

Detects:

EBS volumes not attached to EC2 instances

Why important:
Unused storage continues generating unnecessary cost.

2. Stopped EC2 Instances

Detects:

EC2 instances in stopped state

Why important:
Stopped instances may still incur storage and infrastructure cost.

Safety note:
Stopped EC2 instances are intentionally excluded from automated deletion because they may represent temporary operational workloads.

3. Unused Elastic IPs

Detects:

Elastic IP addresses not attached to instances

Why important:
Unused Elastic IPs may generate unnecessary charges.

4. Missing Required Tags

Detects resources missing governance tags such as:

Owner
Environment
Project

Why important:
Proper tagging improves:

cost tracking
ownership visibility
governance compliance
Safety Design

The project prioritizes safe automation behavior.

Dry-Run Mode

The scanner runs in dry-run mode by default.

Example:

python janitor/janitor.py

This only reports findings without deleting resources.

Explicit Delete Protection

Deletion requires explicit confirmation using:

python janitor/janitor.py --delete

This reduces accidental destructive operations.

Protected Resource Handling

Resources tagged with:

Protected=true

are skipped automatically.

This simulates production-grade protection controls.

Generated Reports

The scanner generates two report formats.

JSON Report

File:

reports/report.json

Purpose:

machine-readable output
CI/CD integration
automation compatibility
Markdown Report

File:

reports/report.md

Purpose:

human-readable reporting
easier review
demo presentation
Example Findings

Example scan results:

- orphaned EBS volume: vol-12345
- stopped EC2 instance: i-12345
- unused Elastic IP
- S3 bucket missing Owner tag
CI/CD Workflow

GitHub Actions automates the complete workflow.

Workflow file:

.github/workflows/cost-janitor.yml
GitHub Actions Pipeline Flow
Step 1 – Start LocalStack

Launch LocalStack container.

Step 2 – Initialize Terraform

Run:

terraform init
Step 3 – Apply Infrastructure

Run:

terraform apply -auto-approve
Step 4 – Execute Cost Janitor

Run:

python janitor/janitor.py
Step 5 – Upload Reports

Generated reports are uploaded as GitHub Actions artifacts.

Demo Walkthrough
Step 1 – Show Infrastructure

Explain:

Terraform files
LocalStack setup
provisioned resources
Step 2 – Run Cost Janitor

Execute:

python janitor/janitor.py

Show detections:

orphaned EBS
stopped EC2
unused EIP
missing tags
Step 3 – Open Generated Reports

Review:

report.json
report.md
Step 4 – Show GitHub Actions Success

Demonstrate:

successful pipeline execution
uploaded artifacts
automation flow
Engineering Decisions
Decision	Reason
LocalStack instead of AWS	Safe local testing
Modular Terraform	Better maintainability
Dry-run by default	Safer automation
Explicit delete flag	Prevent accidental cleanup
Protected tags	Simulated production safeguards
JSON + Markdown reports	Machine + human readability
GitHub Actions integration	CI/CD automation
Known Limitations
S3 Lifecycle Policies

S3 lifecycle configuration was excluded from active LocalStack execution because lifecycle APIs caused repeated timeout behavior in local simulation.

Limited Cloud Coverage

The current implementation focuses on a subset of AWS resources.

Future versions may expand support for:

RDS
Load Balancers
NAT Gateways
EKS resources
Lambda functions
Future Enhancements

Potential improvements:

Slack/MS Teams notifications
automated cleanup approvals
HTML dashboard reporting
policy-as-code integration
multi-account scanning
scheduled scans
cost estimation integration
historical trend tracking
Learning Outcomes

This project demonstrates practical experience with:

Terraform Infrastructure as Code
LocalStack cloud simulation
Python automation scripting
boto3 SDK usage
GitHub Actions CI/CD
cloud governance concepts
cost optimization workflows
modular infrastructure design
safe automation engineering
Key Takeaways

This project prioritizes:

reproducibility
safety
modularity
maintainability
realistic automation workflows

rather than large-scale enterprise complexity.

It serves as a practical demonstration of modern DevOps and SRE engineering practices using fully local cloud simulation.
