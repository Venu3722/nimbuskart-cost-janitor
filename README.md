# README.md

# DevOps Engineer Assignment — Multi-Cloud Cost Hygiene & Automation

## Overview

This project implements a local-first cloud cost hygiene automation platform for NimbusKart using Terraform, LocalStack, Python, and GitHub Actions.

The infrastructure is provisioned using Terraform against LocalStack, creating a staging AWS-like environment that includes:

* VPC networking
* Public subnets
* Security groups
* EC2 web-tier instances
* S3 logging bucket
* Intentionally orphaned EBS resources for testing

A custom Python-based “Cost Janitor” automation scans the environment to detect orphaned or wasteful resources including:

* Unattached EBS volumes
* Stopped EC2 instances
* Unassociated Elastic IPs
* Resources missing required governance tags

GitHub Actions is integrated to continuously enforce infrastructure cost hygiene during pull request validation workflows.

---

## How to run locally

### 1. Clone repository


git clone <your-github-repository-url>
cd nimbuskart-cost-janitor


---

### 2. Start LocalStack

docker run -d -p 4566:4566 -v /var/run/docker.sock:/var/run/docker.sock --name localstack localstack/localstack:3.5


Verify container status:

docker ps


Verify LocalStack health:


curl http://localhost:4566/_localstack/health


---

### 3. Install Terraform Local Wrapper


pip install terraform-local


---

### 4. Initialize and Apply Terraform Infrastructure


cd terraform

tflocal init

tflocal apply -auto-approve


This provisions:

* VPC
* Public subnets
* Internet gateway
* Security groups
* EC2 instances
* S3 bucket
* Orphaned EBS volume

---

### 5. Install Python Dependencies


cd ../janitor

pip install -r requirements.txt


---

### 6. Run Cost Janitor (Dry Run)

Dry-run mode scans resources without deleting them.

```bash id="jlwm52"
python janitor.py --dry-run
```

Generated artifacts:

* `report.json`
* `report.md`

If orphaned resources are detected, the script intentionally exits with status code `1` to fail CI/CD workflows appropriately.

---

### 7. Run Cost Janitor (Delete Mode)

Delete mode removes orphaned resources unless protected using:


Protected=true

Execution:


python janitor.py --delete


## Architecture


                    +----------------------+
                    |   GitHub Actions     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |     LocalStack       |
                    |  (Mock AWS APIs)     |
                    +----------+-----------+
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
     +--------------+                  +-------------------+
     | Terraform IaC|                  |   Cost Janitor    |
     | Infrastructure|                 |   janitor.py      |
     +--------------+                  +-------------------+
                                                  |
                                                  v
                                +--------------------------------+
                                | report.json + report.md output |
                                +--------------------------------+
```

---

## Decisions & deviations

* SSH access remains configurable because exposing port 22 publicly using `0.0.0.0/0` is unsafe for production environments.
* The Cost Janitor operates in `--dry-run` mode by default to avoid accidental destructive actions.
* Resources tagged with `Protected=true` are excluded from automated deletion workflows.
* Static pricing constants were used because LocalStack does not expose AWS Billing APIs.
* Missing tag validation was implemented to support future FinOps governance enforcement.
* LocalStack EC2 emulation on Windows environments showed intermittent instability; therefore graceful fallback handling was implemented for resilient scanning workflows.
* AWS was implemented fully while future GCP and Azure extensibility is documented in `DESIGN.md`.

---

## Trade-offs

Given additional implementation time, the following improvements would be added:

* Multi-cloud provider abstraction layer for AWS, GCP, and Azure
* Slack or email alert integrations
* Historical cost trend persistence using DynamoDB
* Prometheus and Grafana observability integration
* Automated remediation approval workflows
* Snapshot age and unused AMI analysis
* Parallelized scanning for large cloud environments
* Terraform remote state management
* Expanded unit and integration test coverage

---

## AI usage disclosure

AI tools used during development:

* ChatGPT for Terraform structure guidance, boto3 debugging assistance, and GitHub Actions troubleshooting
* GitHub Copilot for boilerplate autocomplete and workflow acceleration

One incorrect AI suggestion involved unsupported LocalStack provider endpoint configurations, which was identified during testing and corrected manually.

The orphan detection logic, deletion safety controls, reporting workflow, and tagging validation inside `janitor.py` were reviewed, modified, and validated manually to ensure operational correctness and engineering understanding.
