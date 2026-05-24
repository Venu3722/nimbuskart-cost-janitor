# Submission — DevOps Engineer Assignment

**Candidate name:** Venu Vellasiri

**Email:** venu74447@gmail.com

**Date submitted:** 24-05-2026

**Hours spent (approximate):** 8-10

---

## Deliverables checklist

* [x] Part A: Terraform code under /terraform applies cleanly on LocalStack
* [x] Part A: `terraform validate` and `terraform fmt -check` both pass
* [x] Part B: Janitor script runs in --dry-run mode and produces report.json
* [x] Part B: GitHub Actions workflow runs green on a fresh PR
* [x] Part B: --delete mode respects Protected=true tag
* [x] Part C: DESIGN.md is present and within 2 pages
* [x] Walkthrough video link below is accessible (unlisted is fine)

---

## Walkthrough video

Link (Loom / YouTube unlisted / Google Drive):

Length: max 5 minutes

---

## Sample report

Path to a sample report.json produced by your script:

```txt
samples/report.example.json
```

---

## Known limitations

* LocalStack EC2 emulation may behave inconsistently on Windows environments.
* Static pricing estimates are approximate and based on public AWS pricing references.
* LocalStack does not expose real AWS billing APIs.
* Workflow testing was primarily performed on Linux-based GitHub runners.
* Multi-cloud provider support is documented architecturally but not fully implemented.

---

## AI usage disclosure

* ChatGPT was used for Terraform structure guidance, boto3 debugging assistance, LocalStack troubleshooting, and GitHub Actions workflow refinement.
* GitHub Copilot was used for boilerplate autocomplete and workflow acceleration.
* All generated code was manually reviewed, modified, tested, and validated before submission.
