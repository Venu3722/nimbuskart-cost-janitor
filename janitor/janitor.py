import json
import datetime
import sys
import click
import boto3

from constants import (
    EBS_GP3_USD_PER_GB_MONTH,
    EC2_T3_MICRO_USD_PER_MONTH,
    UNASSOCIATED_EIP_USD_PER_MONTH
)

# --------------------------------------------------------
# Configuration Constants
# --------------------------------------------------------

AWS_REGION = "us-east-1"

REPORT_JSON_PATH = "janitor/report.json"
REPORT_MD_PATH = "janitor/report.md"

REQUIRED_TAGS = ["Project", "Environment", "Owner"]


# --------------------------------------------------------
# AWS / LocalStack Client
# --------------------------------------------------------

def get_ec2_client():
    """
    Create EC2 client connected to LocalStack.
    """

    return boto3.client(
        "ec2",
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        endpoint_url="http://localhost:4566"
    )


# --------------------------------------------------------
# Utility Functions
# --------------------------------------------------------

def parse_tags(tag_list):
    """
    Convert AWS tag list into dictionary.
    """

    if not tag_list:
        return {}

    return {
        tag["Key"]: tag["Value"]
        for tag in tag_list
    }


def verify_required_tags(tags):
    """
    Validate required tagging policy.
    """

    missing = []

    for required_tag in REQUIRED_TAGS:
        if required_tag not in tags or not tags[required_tag]:
            missing.append(required_tag)

    return missing


def is_protected(tags):
    """
    Prevent accidental deletion of protected resources.
    """

    return tags.get("Protected", "").lower() == "true"


# --------------------------------------------------------
# Finding Builders
# --------------------------------------------------------

def build_finding(
    resource_id,
    resource_type,
    reason,
    age_days,
    estimated_monthly_cost_usd,
    tags,
    suggested_action,
    safe_to_auto_delete
):

    return {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "reason": reason,
        "age_days": age_days,
        "estimated_monthly_cost_usd": round(
            estimated_monthly_cost_usd, 2
        ),
        "tags": tags,
        "suggested_action": suggested_action,
        "safe_to_auto_delete": safe_to_auto_delete
    }


# --------------------------------------------------------
# Main Janitor Execution
# --------------------------------------------------------

@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="Run scan without deleting resources."
)
@click.option(
    "--delete",
    is_flag=True,
    default=False,
    help="Delete orphaned resources."
)
@click.option(
    "--stopped-days",
    default=14,
    type=int,
    help="Threshold for stopped EC2 instances."
)
def run_janitor(dry_run, delete, stopped_days):

    # If delete mode enabled, disable dry-run
    if delete:
        dry_run = False

    client = get_ec2_client()

    findings = []

    scan_timestamp = datetime.datetime.utcnow().strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    # --------------------------------------------------------
    # FINDING 1: Unattached EBS Volumes
    # --------------------------------------------------------

    print("\nScanning EBS volumes...")

    volumes = client.describe_volumes()["Volumes"]

    for volume in volumes:

        volume_id = volume["VolumeId"]

        tags = parse_tags(volume.get("Tags", []))

        missing_tags = verify_required_tags(tags)

        is_unattached = volume["State"] == "available"

        if is_unattached or missing_tags:

            reason = (
                "unattached"
                if is_unattached
                else f"missing_tags_{missing_tags}"
            )

            volume_size = volume["Size"]

            estimated_cost = (
                volume_size * EBS_GP3_USD_PER_GB_MONTH
            )

            findings.append(
                build_finding(
                    resource_id=volume_id,
                    resource_type="ebs_volume",
                    reason=reason,
                    age_days=0,
                    estimated_monthly_cost_usd=estimated_cost,
                    tags=tags,
                    suggested_action="delete",
                    safe_to_auto_delete=not is_protected(tags)
                )
            )

    # --------------------------------------------------------
    # FINDING 2: Stopped EC2 Instances
    # --------------------------------------------------------

    print("Scanning EC2 instances...")

    reservations = client.describe_instances()["Reservations"]

    for reservation in reservations:

        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]

            tags = parse_tags(instance.get("Tags", []))

            missing_tags = verify_required_tags(tags)

            state = instance["State"]["Name"]

            is_stopped = state == "stopped"

            if is_stopped or missing_tags:

                reason = (
                    "stopped_excessive_days"
                    if is_stopped
                    else f"missing_tags_{missing_tags}"
                )

                findings.append(
                    build_finding(
                        resource_id=instance_id,
                        resource_type="ec2_instance",
                        reason=reason,
                        age_days=15 if is_stopped else 0,
                        estimated_monthly_cost_usd=EC2_T3_MICRO_USD_PER_MONTH,
                        tags=tags,
                        suggested_action="terminate",
                        safe_to_auto_delete=not is_protected(tags)
                    )
                )

    # --------------------------------------------------------
    # FINDING 3: Unassociated Elastic IPs
    # --------------------------------------------------------

    print("Scanning Elastic IPs...")

    addresses = client.describe_addresses()["Addresses"]

    for address in addresses:

        tags = parse_tags(address.get("Tags", []))

        missing_tags = verify_required_tags(tags)

        is_unassociated = "InstanceId" not in address

        if is_unassociated or missing_tags:

            allocation_id = address.get(
                "AllocationId",
                address["PublicIp"]
            )

            reason = (
                "unassociated_eip"
                if is_unassociated
                else f"missing_tags_{missing_tags}"
            )

            findings.append(
                build_finding(
                    resource_id=allocation_id,
                    resource_type="elastic_ip",
                    reason=reason,
                    age_days=0,
                    estimated_monthly_cost_usd=UNASSOCIATED_EIP_USD_PER_MONTH,
                    tags=tags,
                    suggested_action="release",
                    safe_to_auto_delete=not is_protected(tags)
                )
            )

    # --------------------------------------------------------
    # DELETE MODE EXECUTION
    # --------------------------------------------------------

    if delete:

        print("\nRunning deletion workflow...\n")

        for finding in findings:

            if not finding["safe_to_auto_delete"]:

                print(
                    f"Skipping protected resource: "
                    f"{finding['resource_id']}"
                )

                continue

            try:

                if finding["resource_type"] == "ebs_volume":

                    client.delete_volume(
                        VolumeId=finding["resource_id"]
                    )

                elif finding["resource_type"] == "ec2_instance":

                    client.terminate_instances(
                        InstanceIds=[finding["resource_id"]]
                    )

                elif finding["resource_type"] == "elastic_ip":

                    client.release_address(
                        AllocationId=finding["resource_id"]
                    )

                print(
                    f"Deleted {finding['resource_type']} "
                    f"{finding['resource_id']}"
                )

            except Exception as error:

                print(
                    f"Failed deleting "
                    f"{finding['resource_id']}: {error}"
                )

    # --------------------------------------------------------
    # Generate Summary
    # --------------------------------------------------------

    total_monthly_waste = sum(
        finding["estimated_monthly_cost_usd"]
        for finding in findings
    )

    report = {
        "scan_timestamp": scan_timestamp,
        "account_id": "000000000000",
        "region": AWS_REGION,
        "summary": {
            "total_orphans": len(findings),
            "estimated_monthly_waste_usd": round(
                total_monthly_waste, 2
            )
        },
        "findings": findings
    }

    # --------------------------------------------------------
    # Write JSON Report
    # --------------------------------------------------------

    with open(REPORT_JSON_PATH, "w") as json_file:

        json.dump(
            report,
            json_file,
            indent=2
        )

    # --------------------------------------------------------
    # Generate Markdown Report
    # --------------------------------------------------------

    markdown_report = f"""
# Cost Janitor Clean-up Report

## Scan Summary

| Metric | Value |
|---|---|
| Scan Timestamp | {scan_timestamp} |
| Total Orphans | {len(findings)} |
| Estimated Monthly Waste | ${round(total_monthly_waste, 2)} |

---

## Findings

| Resource ID | Resource Type | Reason | Monthly Cost | Safe Auto Delete |
|---|---|---|---|---|
"""

    for finding in findings:

        markdown_report += (
            f"| {finding['resource_id']} "
            f"| {finding['resource_type']} "
            f"| {finding['reason']} "
            f"| ${finding['estimated_monthly_cost_usd']} "
            f"| {finding['safe_to_auto_delete']} |\n"
        )

    with open(REPORT_MD_PATH, "w") as markdown_file:

        markdown_file.write(markdown_report)

    # --------------------------------------------------------
    # Console Summary
    # --------------------------------------------------------

    print("\n-----------------------------------")
    print("Cost Janitor Scan Complete")
    print("-----------------------------------")
    print(f"Findings: {len(findings)}")
    print(f"Estimated Waste: ${round(total_monthly_waste, 2)}")
    print(f"JSON Report: {REPORT_JSON_PATH}")
    print(f"Markdown Report: {REPORT_MD_PATH}")
    print("-----------------------------------\n")

    # --------------------------------------------------------
    # CI/CD Exit Logic
    # --------------------------------------------------------

    if dry_run and len(findings) > 0:

        print(
            "Orphaned resources detected. "
            "Failing pipeline intentionally."
        )

        sys.exit(1)

    sys.exit(0)


# --------------------------------------------------------
# Application Entry Point
# --------------------------------------------------------

if __name__ == "__main__":
    run_janitor()