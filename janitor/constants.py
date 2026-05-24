"""
AWS Pricing Constants
Region: us-east-1

Purpose:
These static pricing estimates are used by the Cost Janitor
to estimate potential monthly waste from orphaned resources.

Note:
LocalStack does not expose real AWS Billing APIs,
therefore approximate public AWS pricing values are used.

Pricing references retrieved from official AWS pricing pages.
"""

# --------------------------------------------------------
# EBS gp3 Pricing
# Source:
# https://aws.amazon.com/ebs/pricing/
#
# gp3 storage pricing:
# $0.08 per GB-month (us-east-1)
# --------------------------------------------------------

EBS_GP3_USD_PER_GB_MONTH = 0.08


# --------------------------------------------------------
# EC2 t3.micro Linux On-Demand Pricing
# Source:
# https://aws.amazon.com/ec2/pricing/on-demand/
#
# Approximation:
# ~$0.0104/hour
# ~730 hours/month
# = ~$7.60/month
# --------------------------------------------------------

EC2_T3_MICRO_USD_PER_MONTH = 7.60


# --------------------------------------------------------
# Elastic IP Pricing
# Source:
# https://aws.amazon.com/vpc/pricing/
#
# Unassociated Elastic IP:
# ~$0.005/hour
# ~730 hours/month
# = ~$3.65/month
# --------------------------------------------------------

UNASSOCIATED_EIP_USD_PER_MONTH = 3.65