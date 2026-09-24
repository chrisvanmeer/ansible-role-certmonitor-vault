# ansible-role-certmonitor-vault

[![Lint](https://img.shields.io/github/actions/workflow/status/chrisvanmeer/ansible-role-certmonitor-vault/ci.yml?branch=main&label=CI)](https://github.com/chrisvanmeer/ansible-role-certmonitor-vault/actions/workflows/ci.yml)
[![Galaxy Role](https://img.shields.io/badge/role-certmonitor__vault-blue)](https://galaxy.ansible.com/chrisvanmeer/certmonitor_vault)

An Ansible role to monitor the expiration of static TLS certificates stored on a
HashiCorp Vault **KV v1 / v2** store. For every configured mount it lists all
secrets, checks whether they contain the configured certificate key and builds a
report of the certificates that expire within the configured validity window.

Optionally it sends a single HTML e-mail report with the expiring certificates.

## Key features

- Supports the HashiCorp Vault auth methods `token`, `userpass` and `approle`.
- Validates every secret in every configured KV1/KV2 mount.
- Requires no elevated privileges: the role runs **without `become`**.
- The report e-mail is always sent **from the Ansible control node**
  (`delegate_to: localhost`). The managed hosts do not need any access to the
  SMTP relay; only the machine running Ansible needs to reach it.

## Requirements

Collections (install once on the control node):

```bash
ansible-galaxy collection install -r requirements.yml
```

| Collection | Used for |
| --- | --- |
| `community.hashi_vault` | Vault KV read / listing and token auth |
| `community.crypto` | Certificate inspection (`x509_certificate_info`) |
| `community.general` | Sending the report (`mail`) |
| `community.docker` | Only needed when running the Molecule tests |

Python modules on the control node (and on the target when `delegate_to` is not
used for the Vault calls, e.g. running the role with `local` connection):

- `hvac`
- `requests>=2.29`

## Role variables

All variables are listed below with their default values (see `defaults/main.yml`).
See also `meta/argument_specs.yml` for the machine readable specification.

### Vault connection

```yaml
certmonitor_vault_address: http://127.0.0.1:8200
```

The address of the Vault server, e.g. `https://vault.example.com:8200`.

```yaml
certmonitor_vault_validate_certs: true
```

When using TLS, validate the server certificate. Keep enabled in production.

```yaml
certmonitor_vault_auth_method: approle
```

Supported auth methods: `token`, `userpass` and `approle`.

```yaml
certmonitor_vault_auth_method_mount_point:   # optional
```

Mount point of the auth method when it differs from the default.

Credentials per auth method (required for the selected method):

```yaml
certmonitor_vault_auth_token_token: <token>                            # auth_method: token
certmonitor_vault_auth_userpass_username: <username>                   # auth_method: userpass
certmonitor_vault_auth_userpass_password: <password>                   # auth_method: userpass
certmonitor_vault_auth_approle_role_id: <role_id>                      # auth_method: approle
certmonitor_vault_auth_approle_secret_id: <secret_id>                  # auth_method: approle
```

For security, the role asserts that the credentials (`token`, `userpass`
password and `approle` secret ID) are [Ansible Vault encrypted](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
strings. To accept plain text credentials, e.g. when injecting them through CI/CD
variables:

```yaml
certmonitor_vault_require_encrypted_credentials: true   # set to false to allow plain text
```

### Secrets to monitor

```yaml
certmonitor_vault_list:
  - secrets_engine: kv1            # kv1 or kv2 - required
    secrets_engine_mount_point: my_kv_mount   # optional, when the mount is not the default
    secret_key: certificate      # key holding the PEM certificate - required
```

Every secret in every configured mount is checked for the given `secret_key`.

### Validity check

```yaml
certmonitor_vault_validity_check: "+2w"
```

Validity window reported on. Uses the relative notation of
`community.crypto.x509_certificate_info`, e.g. `+7d`, `+2w`, `+3m`.

### E-mail report

```yaml
certmonitor_vault_email_enabled: false
```

Enable the e-mail report. It is always sent from the Ansible control node, so
the SMTP relay only needs to be reachable from the control node.

```yaml
certmonitor_vault_email_subject: "Expiring Vault TLS Certificates"
certmonitor_vault_email_subtype: "html"     # html or plain (adjust the template for plain)
```

SMTP / recipients (all optional, omitted when not set):

```yaml
certmonitor_vault_smtp_server: mail.example.com
certmonitor_vault_smtp_port: 25
certmonitor_vault_smtp_username:
certmonitor_vault_smtp_password:
certmonitor_vault_smtp_secure: try          # never | always | starttls | try
certmonitor_vault_smtp_timeout: 30
certmonitor_vault_email_sender: certmonitor@example.com
certmonitor_vault_email_recipient: ops@example.com
certmonitor_vault_email_recipient_cc:
certmonitor_vault_email_recipient_bcc:
certmonitor_vault_email_headers:
  Reply-To: security@example.com
```

The report is only sent when there is at least one expiring certificate.

## Example playbook

```yaml
- name: Certificate Monitoring - HashiCorp Vault
  hosts: all
  gather_facts: true

  roles:
    - role: chrisvanmeer.certmonitor_vault
      vars:
        certmonitor_vault_address: https://vault.domain.org:8200
        certmonitor_vault_auth_method: approle
        certmonitor_vault_auth_approle_role_id: 8c035e48-c065-ba00-7e29-73a387f5938b
        certmonitor_vault_auth_approle_secret_id: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          31333138656334333062623162303539616634376661333530326138613439656362313037316631
          3666343965316236393230313939643963623736656464330a376161626639656137333135656236
          63616430333338613761373733613261346332636334383334613462356136636661366365363162
          6263636334666231350a623238376261613337653766353862363836346164383364356138313765
          37313238333065346263333961636161326639326161383739313431353537626630373535666436
          3938383230356338333836353933326330363833653766316530
        certmonitor_vault_list:
          - secrets_engine: kv1
            secrets_engine_mount_point: cert_kv1_1
            secret_key: certificate
          - secrets_engine: kv2
            secrets_engine_mount_point: cert_kv2_1
            secret_key: certificate
        certmonitor_vault_email_enabled: true
        certmonitor_vault_smtp_server: mail.example.com
        certmonitor_vault_smtp_port: 587
        certmonitor_vault_smtp_secure: starttls
        certmonitor_vault_email_sender: certmonitor@example.com
        certmonitor_vault_email_recipient: ops@example.com
```

> *No `become` is required*: the role only talks to the Vault HTTP API and sends
> e-mail from the control node.

## Development

The role uses [Molecule](https://ansible.readthedocs.io/projects/molecule/) with
the Docker driver for functional testing:

```bash
pip install ansible-core molecule molecule-plugins[docker] aiosmtpd
ansible-galaxy collection install -r requirements.yml
molecule test -s default   # certificate detection (KV1 + KV2)
molecule test -s email     # report e-mail sent from the control node
```

The `default` scenario spins up a Vault dev server and a managed host, writes
expiring and valid certificates into KV1/KV2 mounts and verifies the report. The
`email` scenario additionally starts a local SMTP capture server on the control
node and asserts that the e-mail is sent from the controller, not from the
managed host.

Linting is enforced with `ansible-lint` and `yamllint` and runs in CI
(`.github/workflows/ci.yml`) together with the Molecule scenarios. On a `v*`
tag push, lint and tests must pass before the role is imported into
[Ansible Galaxy](https://galaxy.ansible.com/chrisvanmeer/certmonitor_vault)
using the `GALAXY_API_KEY` secret:

```bash
ansible-galaxy role import chrisvanmeer ansible-role-certmonitor-vault --token "$GALAXY_API_KEY"
```

## License

BSD

## Author

- Chris van Meer [@chrisvanmeer](https://github.com/chrisvanmeer) `c.v.meer@atcomputing.nl`
