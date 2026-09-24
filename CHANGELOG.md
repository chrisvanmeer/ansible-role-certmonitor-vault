# Changelog

## [Unreleased]

### Fixed

- The plain-text credential asserts (`token`, `userpass` password and `approle`
  secret ID) now only run when `certmonitor_vault_require_encrypted_credentials`
  is disabled, instead of always running before the `vault_encrypted`
  enforcement assert.

## [1.1.0] - 2026-09-24

### Changed

- The report e-mail is now always sent from the Ansible control node
  (`delegate_to: localhost`), which requires no `become` and no SMTP access from
  the managed hosts.
- Dropped the `jmespath` dependency by replacing `json_query` with native
  `selectattr` filtering.
- The `days_to_expiration` value no longer depends on `ansible_date_time` facts;
  it is computed from the UTC clock on the control node.
- All intermediate facts are reset at the start of the role, making repeated
  invocation of the role within a single play safe.
- The role now exits cleanly when `certmonitor_vault_list` is undefined or empty.
- E-mail and SMTP variables are documented and validated; the misleading
  `certmonitor_email_enabled` comment was fixed to
  `certmonitor_vault_email_enabled`.
- Added `meta/argument_specs.yml` with the machine readable role specification.
- Added `requirements.yml`, `LICENSE`, `CHANGELOG.md` and `.gitignore`.
- Updated tooling: `ansible-lint` 26.x and `yamllint`.

### Added

- Molecule functional tests (`default` and `email` scenarios) using a real
  Vault dev server with KV1 and KV2 mounts.
- CI workflow: lint, Molecule tests on every push/PR, and automatic import into
  Ansible Galaxy on `v*` tags using the `GALAXY_API_KEY` secret.
- `certmonitor_vault_require_encrypted_credentials` toggle so credentials can be
  injected as plain text in CI/CD or tests.

### Fixed

- The `certmonitor_vault_auth_method_mount_point` assertion tested the wrong
  variable (`secrets_engine` instead of `secrets_engine_mount_point`).
- The address assertion required a port and rejected valid URLs; a port is now
  optional.

## [1.0.0] - 2024-11-21

- Initial release of the certificate monitoring role.
