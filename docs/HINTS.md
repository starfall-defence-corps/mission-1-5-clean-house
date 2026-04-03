# Mission 1.5: Clean House — Hints & Troubleshooting Guide

**Rank**: Ensign Candidate (Minimal Scaffolding)

You are close to Ensign. Fewer hints. More judgement calls.

---

## Role Structure

**After `ansible-galaxy init roles/fleet_hardening`, you get:**

```
roles/fleet_hardening/
  README.md
  defaults/main.yml
  files/
  handlers/main.yml
  meta/main.yml
  tasks/main.yml
  templates/
  tests/
  vars/main.yml
```

Edit the files you need. Leave the rest as defaults.

**Where things go:**

| Content | File |
|---------|------|
| SSH hardening tasks, firewall tasks | `tasks/main.yml` |
| SSH restart handler | `handlers/main.yml` |
| sshd_config.j2, motd.j2 | `templates/` |
| Default SSH settings, banner text | `defaults/main.yml` |
| OS-specific overrides | `group_vars/debian.yml`, `group_vars/redhat.yml` |

**Template paths in roles:**

When a task in a role uses `template`, the `src` path is relative to the role's `templates/` directory:

```yaml
# In roles/fleet_hardening/tasks/main.yml:
- name: Deploy SSH config
  ansible.builtin.template:
    src: sshd_config.j2     # ← looks in roles/fleet_hardening/templates/
    dest: /etc/ssh/sshd_config
```

You do NOT need `templates/sshd_config.j2` — just `sshd_config.j2`.

---

## Vault

**Creating a vault file:**

```bash
# Method 1: Create interactively (opens editor)
ansible-vault create vault.yml

# Method 2: Create plaintext, then encrypt
echo 'vault_my_var: my_value' > vault.yml
ansible-vault encrypt vault.yml
```

**Editing an encrypted file:**

```bash
ansible-vault edit vault.yml
```

**Viewing encrypted contents:**

```bash
ansible-vault view vault.yml
```

**The vault password file:**

`ansible.cfg` has `vault_password_file = .vault-pass`. Create this file with your vault password:

```bash
echo 'your-password-here' > .vault-pass
chmod 600 .vault-pass
```

This file is in `.gitignore` — it never goes to version control.

**Referencing vault variables:**

In `site.yml`:
```yaml
- name: My Play
  hosts: all
  vars_files:
    - vault.yml
  roles:
    - fleet_hardening
```

The vault variables are now available to the role. You can reference them in `defaults/main.yml`:

```yaml
banner_message: "{{ vault_banner_message }}"
```

---

## Common Issues

**"Decryption failed" error:**

Your `.vault-pass` file content doesn't match the password used to encrypt `vault.yml`. Either:
- Re-create `.vault-pass` with the correct password
- Re-create `vault.yml` with the password in `.vault-pass`

**"ERROR! the role 'fleet_hardening' was not found":**

Check that:
1. The role is at `workspace/roles/fleet_hardening/` (not `workspace/fleet_hardening/`)
2. `ansible.cfg` has `roles_path = roles`
3. You're running from the `workspace/` directory

**"No vars_files found" or vault error:**

Ensure `vault.yml` is in the `workspace/` directory (same level as `site.yml`).

---

## CRITICAL SPOILER — Full Solution

> **STOP.** Last resort only.

<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>

**roles/fleet_hardening/defaults/main.yml:**
```yaml
---
ssh_permit_root_login: "no"
ssh_password_authentication: "no"
ssh_login_grace_time: "{{ vault_ssh_login_grace_time | default(30) }}"
ssh_max_auth_tries: 3
ssh_service_name: ssh
banner_message: "{{ vault_banner_message | default('STARFALL DEFENCE CORPS') }}"
firewall_pkg: ufw
```

**roles/fleet_hardening/tasks/main.yml:**
```yaml
---
- name: Deploy SSH configuration
  ansible.builtin.template:
    src: sshd_config.j2
    dest: /etc/ssh/sshd_config
    owner: root
    group: root
    mode: '0644'
    validate: 'sshd -t -f %s'
  notify: Restart SSH

- name: Deploy login banner
  ansible.builtin.template:
    src: motd.j2
    dest: /etc/motd
    owner: root
    group: root
    mode: '0644'

- name: Install firewall (Debian)
  ansible.builtin.apt:
    name: "{{ firewall_pkg }}"
    state: present
  when: ansible_os_family == "Debian"

- name: Install firewall (RedHat)
  ansible.builtin.dnf:
    name: "{{ firewall_pkg }}"
    state: present
  when: ansible_os_family == "RedHat"

- name: Allow SSH through firewall (Debian)
  community.general.ufw:
    rule: allow
    port: '22'
    proto: tcp
  when: ansible_os_family == "Debian"

- name: Allow SSH through firewall (RedHat)
  ansible.posix.firewalld:
    service: ssh
    permanent: true
    immediate: true
    state: enabled
  when: ansible_os_family == "RedHat"

- name: Enable firewall (Debian)
  community.general.ufw:
    state: enabled
  when: ansible_os_family == "Debian"

- name: Enable firewall (RedHat)
  ansible.builtin.service:
    name: firewalld
    state: started
    enabled: true
  when: ansible_os_family == "RedHat"
```

**roles/fleet_hardening/handlers/main.yml:**
```yaml
---
- name: Restart SSH
  ansible.builtin.service:
    name: "{{ ssh_service_name }}"
    state: restarted
```

**roles/fleet_hardening/templates/sshd_config.j2:**
```jinja2
# {{ ansible_managed }}
PermitRootLogin {{ ssh_permit_root_login }}
PasswordAuthentication {{ ssh_password_authentication }}
PubkeyAuthentication yes
LoginGraceTime {{ ssh_login_grace_time }}
MaxAuthTries {{ ssh_max_auth_tries }}
Protocol 2
SyslogFacility AUTH
LogLevel INFO
X11Forwarding no
PrintMotd yes
AcceptEnv LANG LC_*
Subsystem sftp /usr/libexec/openssh/sftp-server
```

**roles/fleet_hardening/templates/motd.j2:**
```jinja2

===============================================
  {{ banner_message }}
===============================================
  Hostname : {{ ansible_hostname }}
  OS       : {{ ansible_distribution }} {{ ansible_distribution_version }}
===============================================
  Unauthorised access is prohibited.
===============================================
```

**workspace/site.yml:**
```yaml
---
- name: Clean House — Fleet Hardening Role
  hosts: all
  become: true
  vars_files:
    - vault.yml
  roles:
    - fleet_hardening
```

**workspace/vault.yml** (before encryption):
```yaml
vault_ssh_login_grace_time: 30
vault_banner_message: "STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY"
```

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
