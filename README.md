ansible-role-certmonitor-vault
========================

A role to monitor the expiration of any static certificates on a HashiCorp Vault's K/V store

Requirements
------------

Ansible collections:

- `community.hashi_vault`

Python modules:

- `hvac`
- `jmespath`
- `requests>=2.29`

Role defaults
-------------

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yml
certmonitor_vault_address: http://127.0.0.1:8200
```

The address of the Vault server.

```yml
certmonitor_vault_validate_certs: true
```

When using TLS, validate certificates. Leave this enabled in production environments.

```yml
certmonitor_vault_auth_method: approle
```

Supported auth methods: token, userpass and approle.

```yml
certmonitor_vault_validity_check: "+2w"
```

The check of the certificates validity specified in weeks from now. By default we use "+2w" to report certificates that expire within the next two weeks.

```yml
certmonitor_vault_email_enabled: false
```

Default email reporting is disabled, set this to `true` to enable.

```yml
certmonitor_vault_email_subject: "Expiring TLS Certificates"
```

Email subject when sending email reports.

```yml
certmonitor_vault_email_subtype: "html"
```

Setting the email mime type to `html`. Can also be set to `plain`. One can modify the template to their choosing to match this.

There are more variables available for the email section. Refer to the last task in the playbook for this. If not existent, these will be omitted, but this gives you the option to include these values in variables, rather than having to edit the playbook.

Dependencies
------------

For the certificate inspection, this role depends on the `community.crypto.x509_certificate_info` module.  
For email, this role depends on the `community.general.mail` module.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

```yml
- name: Certificate Monitoring - HashiCorp Vault
  hosts: all
  become: true

  roles:
    - role: chrisvanmeer.certmonitor_vault
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
```

License
-------

BSD

Author Information
------------------

- Chris van Meer <c.v.meer@atcomputing.nl>
