1. Multi-cloud architecture

To support AWS, GCP, and Azure without rewriting the entire system, the Cost Janitor should follow a provider abstraction architecture.

Recommended structure:

janitor/
├── core/
│   ├── scanner.py
│   ├── reporter.py
│   ├── policies.py
│   └── pricing.py
│
├── providers/
│   ├── aws/
│   ├── gcp/
│   └── azure/

The core layer would contain:

orphan detection workflows
governance validation
deletion policies
report generation
pricing estimation logic

Each cloud provider module would implement:

resource discovery
tag extraction
deletion APIs
provider-specific cost metadata

This architecture enables future cloud providers to be integrated without modifying the core scanning engine.

2. Permissions
Dry-run mode permissions

The Cost Janitor requires read-only access during scanning operations.

Required permissions:

ec2
ec2
ec2
ec2
s3
tag
Delete mode additional permissions

Delete mode requires additional destructive permissions:

ec2
ec2
ec2
ec2
Minimal IAM policy (read-only mode)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "ec2:DescribeSnapshots",
        "tag:GetResources",
        "s3:ListBucket"
      ],
      "Resource": "*"
    }
  ]
}
3. Safety net
Failure Mode 1 — Deleting disaster recovery infrastructure

Stopped EC2 instances may intentionally exist as disaster recovery or standby infrastructure.

Guardrails
Require approval tags such as:
AutoDeleteApproved=true
Enforce minimum age thresholds before deletion
Generate alerts before destructive actions
Require manual approval workflows for production accounts
Failure Mode 2 — Deleting backup storage volumes

Unattached EBS volumes may still contain critical snapshot recovery data.

Guardrails
Prevent deletion of resources tagged:
Protected=true
Introduce quarantine tagging before deletion
Implement multi-stage deletion workflows
4. Observability
Metric	Source	Alert Threshold
orphan_resources_total	Janitor scan	>10
estimated_monthly_waste_usd	Report summary	>$500
janitor_scan_failures	GitHub Actions	Any failure
resources_deleted_total	Janitor logs	Sudden spike
missing_required_tags_total	Tag validator	>5

Recommended monitoring targets:

CloudWatch
Prometheus
Grafana
GitHub Actions workflow logs
5. What was not built

This implementation intentionally excludes real AWS billing integration, centralized authentication systems, distributed scanning, Slack/email notifications, advanced FinOps analytics, historical cost persistence, and enterprise-grade approval workflows.

These features were intentionally scoped out to prioritize infrastructure automation, Terraform provisioning, orphan detection workflows, reporting generation, CI/CD integration, and deletion safety controls within the assignment time constraints.

LocalStack EC2 emulation on Windows environments also introduced intermittent instability during testing, therefore graceful fallback handling was implemented to preserve report generation continuity.