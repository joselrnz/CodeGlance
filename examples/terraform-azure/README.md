# Terraform Azure Example

A small Azure stack used to demo `codeglance` on Terraform modules:

- `main.tf` wires the root resource group, network module, and app module.
- `modules/network/` creates a virtual network and subnet.
- `modules/app/` creates a Linux App Service plan and web app.

Run:

```bash
codeglance examples/terraform-azure
```
