# Mission 1.5: Clean House — E2E Manual Test Script

**Purpose**: Verify the entire student workflow works end-to-end: role creation, vault encryption, deployment.
**Time**: ~25 minutes.
**Prerequisites**: Docker running, ports 2221-2223 free.

---

## 1. Setup

```bash
cd ~/projects/starfall-defence-corps/mission-1-5-clean-house
make destroy 2>/dev/null; true
make setup
```

**Expected**: All 3 nodes ONLINE (2 Ubuntu + 1 Rocky).

```bash
cd workspace
ansible all -m ping
```

**Expected**: All 3 return `SUCCESS`.

---

## 2. Verify Starting State

```bash
# Colonel's plaintext creds should exist
ansible all -m shell -a "cat /opt/fleet-db-creds.txt"
```

**Expected**: All nodes show `fleet_db_user: admin`, `fleet_db_pass: V01dborn_Hunter_2187`, `fleet_api_key: sk-sdc-...`.

```bash
# SSH still misconfigured
ansible all -m shell -a "grep PermitRootLogin /etc/ssh/sshd_config | head -1"
```

**Expected**: `PermitRootLogin yes` on all nodes.

```bash
# OS families correct
ansible all -m setup -a "filter=ansible_os_family"
```

**Expected**: sdc-web=Debian, sdc-db=RedHat, sdc-comms=Debian.

---

## 3. Run ARIA Before Solution

```bash
cd ..
make test
cd workspace
```

**Expected**: Phase 1 fails (role directory does not exist). Everything else skips.

---

## 4. Create the Role

```bash
ansible-galaxy init roles/fleet_hardening
```

**Expected**: Directory structure created at `roles/fleet_hardening/`.

```bash
ls roles/fleet_hardening/
```

**Expected**: `defaults  files  handlers  meta  README.md  tasks  templates  tests  vars`

---

## 5. Populate Role Files

### defaults/main.yml

```bash
cat > roles/fleet_hardening/defaults/main.yml << 'EOF'
---
ssh_permit_root_login: "no"
ssh_password_authentication: "no"
ssh_login_grace_time: "{{ vault_ssh_login_grace_time | default(30) }}"
ssh_max_auth_tries: 3
ssh_service_name: ssh
banner_message: "{{ vault_banner_message | default('STARFALL DEFENCE CORPS') }}"
firewall_pkg: ufw
EOF
```

### group_vars

```bash
cat > inventory/group_vars/all.yml << 'EOF'
---
# Shared variables loaded from vault via site.yml vars_files
EOF

cat > inventory/group_vars/debian.yml << 'EOF'
---
ssh_service_name: ssh
firewall_pkg: ufw
EOF

cat > inventory/group_vars/redhat.yml << 'EOF'
---
ssh_service_name: sshd
firewall_pkg: firewalld
EOF
```

### tasks/main.yml

```bash
cat > roles/fleet_hardening/tasks/main.yml << 'EOF'
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
EOF
```

### handlers/main.yml

```bash
cat > roles/fleet_hardening/handlers/main.yml << 'EOF'
---
- name: Restart SSH
  ansible.builtin.service:
    name: "{{ ssh_service_name }}"
    state: restarted
EOF
```

### templates

```bash
cat > roles/fleet_hardening/templates/sshd_config.j2 << 'EOF'
# {{ ansible_managed }}
# Starfall Defence Corps — SSH Hardening Configuration

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
EOF

cat > roles/fleet_hardening/templates/motd.j2 << 'EOF'

===============================================
  {{ banner_message }}
===============================================
  Hostname : {{ ansible_hostname }}
  OS       : {{ ansible_distribution }} {{ ansible_distribution_version }}
  OS Family: {{ ansible_os_family }}
===============================================
  Unauthorised access is prohibited.
  All activity is monitored and logged.
===============================================
EOF
```

### meta/main.yml

```bash
cat > roles/fleet_hardening/meta/main.yml << 'EOF'
---
galaxy_info:
  author: "SDC Academy"
  description: "Fleet hardening role — SSH, firewall, templates"
  license: MIT
  min_ansible_version: "2.14"
  platforms:
    - name: Ubuntu
      versions: ["22.04"]
    - name: EL
      versions: ["9"]
dependencies: []
EOF
```

---

## 6. Create Vault

```bash
# Create vault password file
echo 'starfall-academy-2187' > .vault-pass
chmod 600 .vault-pass

# Create vault contents and encrypt
cat > vault.yml << 'EOF'
vault_ssh_login_grace_time: 30
vault_banner_message: "STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY"
EOF
ansible-vault encrypt vault.yml
```

**Expected**: `Encryption successful`. File now starts with `$ANSIBLE_VAULT;`.

```bash
# Verify encryption
head -1 vault.yml
```

**Expected**: `$ANSIBLE_VAULT;1.1;AES256`

```bash
# Verify decryption works
ansible-vault view vault.yml
```

**Expected**: Shows plaintext `vault_ssh_login_grace_time: 30` and `vault_banner_message: ...`.

---

## 7. Uncomment site.yml

```bash
cat > site.yml << 'EOF'
---
- name: Clean House — Fleet Hardening Role
  hosts: all
  become: true
  vars_files:
    - vault.yml
  roles:
    - fleet_hardening
EOF
```

---

## 8. Syntax Check

```bash
ansible-playbook site.yml --syntax-check
```

**Expected**: No errors.

---

## 9. Dry Run

```bash
ansible-playbook site.yml --check --diff
```

**Expected**: Shows predicted changes. Vault decryption works automatically via `.vault-pass`.

---

## 10. Execute (First Run)

```bash
ansible-playbook site.yml
```

**Expected**:
- SSH template deployed, handler restarts SSH on all nodes
- MOTD deployed on all nodes
- Firewall installed/configured (conditional tasks skip correctly)
- Play recap shows changes

---

## 11. Verify Changes

```bash
# SSH hardened on all OS families
ansible all -m shell -a "grep PermitRootLogin /etc/ssh/sshd_config"
```
**Expected**: `PermitRootLogin no` on all nodes.

```bash
# MOTD with vault variable
ansible all -m shell -a "cat /etc/motd"
```
**Expected**: Contains `STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY` and host-specific facts.

```bash
# Firewalls active
ansible debian -m shell -a "ufw status | head -1"
```
**Expected**: `Status: active`

```bash
ansible redhat -m shell -a "systemctl is-active firewalld"
```
**Expected**: `active`

---

## 12. Idempotency Check

```bash
ansible-playbook site.yml
```

**Expected**: `changed=0` on ALL hosts.

---

## 13. Full ARIA Verification

```bash
cd ..
make test
```

**Expected**: All 4 phases pass. "Mission 1.5 status: COMPLETE".

---

## 14. Edge Case Tests

### 14a. Plaintext secrets detection

```bash
cd workspace
# Plant a plaintext secret in a visible file
echo "fleet_db_pass: V01dborn_Hunter_2187" > bad-secrets.yml
cd ..
make test 2>&1 | grep -E "(plaintext|secrets|✗)"
```

**Expected**: Phase 2 (Vault) fails — plaintext secrets detected in `bad-secrets.yml`.

```bash
cd workspace
rm bad-secrets.yml
```

### 14b. Unencrypted vault.yml

```bash
ansible-vault decrypt vault.yml
cd ..
make test 2>&1 | grep -E "(encrypted|NOT|✗)"
```

**Expected**: Phase 2 fails — `vault.yml is NOT encrypted`.

```bash
cd workspace
ansible-vault encrypt vault.yml
```

### 14c. Missing .vault-pass

```bash
mv .vault-pass /tmp/vault-pass.bak
ansible-playbook site.yml 2>&1 | tail -5
```

**Expected**: Decryption failure — cannot read vault password file.

```bash
mv /tmp/vault-pass.bak .vault-pass
```

### 14d. Missing role directory

```bash
mv roles /tmp/roles.bak
cd ..
make test 2>&1 | grep -E "(role|not found|✗)"
```

**Expected**: Phase 1 fails — role directory does not exist.

```bash
cd workspace
mv /tmp/roles.bak roles
```

### 14e. Empty tasks/main.yml

```bash
cp roles/fleet_hardening/tasks/main.yml /tmp/tasks.bak
echo "---" > roles/fleet_hardening/tasks/main.yml
cd ..
make test 2>&1 | grep -E "(empty|tasks|✗)"
```

**Expected**: Phase 1 fails — tasks/main.yml is empty.

```bash
cd workspace
cp /tmp/tasks.bak roles/fleet_hardening/tasks/main.yml
```

### 14f. site.yml doesn't reference role

```bash
cat > site.yml << 'EOF'
---
- name: No role here
  hosts: all
  become: true
  tasks:
    - name: Placeholder
      ansible.builtin.debug:
        msg: "no role"
EOF
cd ..
make test 2>&1 | grep -E "(fleet_hardening|role|✗)"
```

**Expected**: Phase 3 fails — site.yml does not reference fleet_hardening role.

```bash
cd workspace
cat > site.yml << 'EOF'
---
- name: Clean House — Fleet Hardening Role
  hosts: all
  become: true
  vars_files:
    - vault.yml
  roles:
    - fleet_hardening
EOF
```

### 14g. Full recovery

```bash
cd ..
make reset
cd workspace
ansible-playbook site.yml
cd ..
make test
```

**Expected**: All phases pass.

---

## 15. Vault Variable Integration Test

```bash
cd workspace
# Change vault value and verify it propagates
ansible-vault decrypt vault.yml
sed -i 's/vault_ssh_login_grace_time: 30/vault_ssh_login_grace_time: 15/' vault.yml
ansible-vault encrypt vault.yml
ansible-playbook site.yml
ansible all -m shell -a "grep LoginGraceTime /etc/ssh/sshd_config"
```

**Expected**: `LoginGraceTime 15` on all nodes. Proves vault variables flow through to templates.

```bash
# Restore
ansible-vault decrypt vault.yml
sed -i 's/vault_ssh_login_grace_time: 15/vault_ssh_login_grace_time: 30/' vault.yml
ansible-vault encrypt vault.yml
ansible-playbook site.yml
```

---

## 16. Cleanup

```bash
cd ..
make destroy
```

---

## Test Summary

| # | Test | Expected |
|---|------|----------|
| 1 | Setup | 3 nodes online (mixed OS) |
| 2 | Starting state | Misconfigs + Colonel's plaintext creds |
| 3 | ARIA before | Role not found, everything fails/skips |
| 4-5 | Create role + populate | Files created correctly |
| 6 | Create vault | Encrypted successfully |
| 7-9 | site.yml + syntax + dry run | No errors |
| 10 | First run | Changes applied via role |
| 11 | Verify changes | SSH, MOTD, firewalls all correct |
| 12 | Second run | changed=0 |
| 13 | ARIA after | All phases pass |
| 14a | Plaintext secret planted | Detected by ARIA |
| 14b | Unencrypted vault | Detected by ARIA |
| 14c | Missing .vault-pass | Decryption failure |
| 14d | Missing role dir | Phase 1 fails |
| 14e | Empty tasks | Phase 1 fails |
| 14f | No role in site.yml | Phase 3 fails |
| 14g | Recovery | Full pass after fix |
| 15 | Vault variable flow | Change propagates to template |
| 16 | Cleanup | Torn down |
