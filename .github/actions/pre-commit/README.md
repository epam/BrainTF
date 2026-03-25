# Do not release this to opensource

Wrapper around the following actions to run pre-commit checks on Terraform code: <https://github.com/clowdhaus/terraform-composite-actions/blob/main/pre-commit/README.md>

## Why do we need this?

The wrapper resolves an issue with removing binaries from `/usr/bin` without `sudo`, but installing them using `sudo`. This leads to issues with self-hosted runner as it shares the same VM.

Do not release this action to opensource, as it is a workaround for using self-hosted runners.

