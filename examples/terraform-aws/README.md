# Terraform AWS Example

A small Terraform stack used to demo `codeglance` on infrastructure code:

- `main.tf` — provider, the `network` module call, a security group, and a web EC2 instance
- `variables.tf` / `outputs.tf` — root inputs and outputs
- `modules/network/` — a reusable VPC + subnet + internet-gateway module

Run: `codeglance examples/terraform-aws`
