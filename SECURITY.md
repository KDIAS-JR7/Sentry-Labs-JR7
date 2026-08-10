# Security Notice

## Lab Credentials

The configuration files, playbooks, and journal entries in this repository contain
**disposable credentials** used only inside a virtualised GNS3 lab environment:

- Username: `admin`
- Password: `cisco` / `cisco123`
- API keys referenced in the AI scripts are loaded from a local `.env` file and are
  **not** committed to this repository.

These are throwaway lab credentials for emulated Cisco IOS devices that exist only
inside GNS3. They were never used against production equipment and should never be
reused in any real environment.

## Best Practice

In any real deployment:

- Never commit credentials or secrets to a repository.
- Use vaults (e.g. Ansible Vault), secret managers, or environment variables.
- Rotate credentials regularly and scope them to least privilege.
