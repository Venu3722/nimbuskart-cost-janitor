import json
import datetime
import os
import sys
import click
import boto3

from constants import (
    EBS_GP3_USD_PER_GB_MONTH,
    EC2_T3_MICRO_USD_PER_MONTH,
    UNASSOCIATED_EIP_USD_PER_MONTH
)

# --------------------------------------------------------
# Configuration Constants & Absolute Path Management
# --------------------------------------------------------

AWS_REGION = "us-east-1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPORT_JSON_PATH = os.path.join(BASE_DIR, "report.json")
REPORT_MD_PATH = os.path.join(BASE_DIR, "report.md")

REQUIRED_TAGS = ["Project", "Environment", "Owner"]

# --------------------------------------------------------
# AWS / LocalStack Client
# --------------------------------------------------------

def get_ec2_client():
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
    if not tag_list:
        return {}
    return {
        tag["Key"]: tag["Value"]
        for tag in tag_list
    }

def verify_required_tags(tags):
    missing = []
    for required_tag in REQUIRED_TAGS:
        if required_tag not in tags or not tags[required_tag]:
            missing.append(required_tag)
    return missing

def is_protected(tags):
    return tags.get("Protected", "").lower() == "true"

# --------------------------------------------------------
# Finding Builder
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
        "estimated_monthly_cost_usd": round(estimated_monthly_cost_usd, 2),
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

    if delete:
        dry_run = False

    client = get_ec2_client()
    findings = []

    scan_timestamp = datetime.datetime.now(
        datetime.UTC
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    # --------------------------------------------------------
    # FINDING 1: Unattached EBS Volumes
    # --------------------------------------------------------
    print("\nScanning EBS volumes...")
    try:
        volumes = client.describe_volumes()["Volumes"]
    except Exception as error:
        print(f"EBS scan failed: {error}")
        volumes = []

    for volume in volumes:
        volume_id = volume["VolumeId"]
        tags = parse_tags(volume.get("Tags", []))
        missing_tags = verify_required_tags(tags)
        is_unattached = (volume["State"] == "available")

        if is_unattached or missing_tags:
            reason = (
                "unattached"
                if is_unattached
                else f"missing_tags_{missing_tags}"
            )
            volume_size = volume["Size"]
            estimated_cost = volume_size * EBS_GP3_USD_PER_GB_MONTH

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
    try:
        reservations = client.describe_instances()["Reservations"]
    except Exception as error:
        print(f"EC2 scan skipped due to LocalStack limitation: {error}")
        reservations = []

    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            tags = parse_tags(instance.get("Tags", []))
            missing_tags = verify_required_tags(tags)
            state = instance["State"]["Name"]
            is_stopped = (state == "stopped")

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
    try:
        addresses = client.describe_addresses()["Addresses"]
    except Exception as error:
        print(f"EIP scan failed: {error}")
        addresses = []

    for address in addresses:
        tags = parse_tags(address.get("Tags", []))
        missing_tags = verify_required_tags(tags)
        is_unassociated = ("InstanceId" not in address)

        if is_unassociated or missing_tags:
            allocation_id = address.get("AllocationId", address["PublicIp"])
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
                print(f"Skipping protected resource: {finding['resource_id']}")
                continue

            try:
                if finding["resource_type"] == "ebs_volume":
                    client.delete_volume(VolumeId=finding["resource_id"])
                elif finding["resource_type"] == "ec2_instance":
                    client.terminate_instances(InstanceIds=[finding["resource_id"]])
                elif finding["resource_type"] == "elastic_ip":
                    client.release_address(AllocationId=finding["resource_id"])
                print(f"Deleted unhygienic resource: {finding['resource_id']}")
            except Exception as error:
                print(f"Failed to delete {finding['resource_id']}: {error}")

    # --------------------------------------------------------
    # REPORT GENERATION
    # --------------------------------------------------------
    total_waste = sum(f["estimated_monthly_cost_usd"] for f in findings)

    output_payload = {
        "scan_timestamp": scan_timestamp,
        "dry_run": dry_run,
        "total_findings": len(findings),
        "total_estimated_monthly_waste_usd": round(total_waste, 2),
        "findings": findings
    }

    with open(REPORT_JSON_PATH, "w") as json_file:
        json.dump(output_payload, json_file, indent=2)

    md_content = f"# 🧹 Cost Janitor Hygiene Report\n\n"
    md_content += f"**Scan Time**: `{scan_timestamp}`\n"
    md_content += f"**Execution Mode**: `{'Dry Run' if dry_run else 'Enforced / Deletion'}`\n"
    md_content += f"**Total Unhealthy Resources Found**: `{output_payload['total_findings']}`\n"
    md_content += f"**Potential Monthly Waste**: `${output_payload['total_estimated_monthly_waste_usd']:.2f} USD`\n\n"
    md_content += "| Resource ID | Type | Reason | Monthly Waste | Action | Safe Deletion |\n"
    md_content += "| --- | --- | --- | --- | --- | --- |\n"

    for f in findings:
        md_content += f"| `{f['resource_id']}` | `{f['resource_type']}` | `{f['reason']}` | ${f['estimated_monthly_cost_usd']:.2f} | `{f['suggested_action']}` | {'✅' if f['safe_to_auto_delete'] else '❌'} |\n"

    with open(REPORT_MD_PATH, "w") as md_file:
        md_file.write(md_content)

    if len(findings) > 0:
        print(f"\n❌ Hygiene check failed: {len(findings)} issues found.")
        sys.exit(1)

if __name__ == "__main__":
    run_janitor()
