---
CLASSIFICATION: CADET EYES ONLY
MISSION: 1.5 — CLEAN HOUSE
DOCUMENT: EXERCISES — Phase-by-Phase Operational Instructions
---

# EXERCISES — MISSION 1.5: CLEAN HOUSE

Complete each phase in sequence. Run `make test` after each phase.

**Scaffolding**: Minimal. You are approaching Ensign rank. The inventory and `ansible.cfg` are provided. The role and vault are yours to create.

---

## PHASE 0: Launch the Fleet

```bash
make setup
```

Then activate the Python environment:

```bash
source venv/bin/activate
```

Your terminal prompt will show `(venv)` when active. You need to do this once per terminal session.

---

## PHASE 1: Intelligence Gathering

> Find Colonel Hardcoded-Password's evidence. Understand what an Ansible role looks like. Plan your role structure.

### Step 1.1 — Find the Colonel's Secrets

```bash
cd workspace
ansible all -m shell -a "cat /opt/fleet-db-creds.txt"
```

You will see plaintext credentials on every node. Database username, password, and an API key — in the open. This is what you are here to prevent.

### Step 1.2 — Understand Role Structure

An Ansible role has a standardised directory layout:

```
roles/fleet_hardening/
  tasks/main.yml        # The role's tasks (your hardening playbook)
  handlers/main.yml     # Handlers (SSH restart, etc.)
  templates/            # Jinja2 templates (sshd_config.j2, motd.j2)
  defaults/main.yml     # Default variable values (lowest precedence)
  vars/main.yml         # Role variables (higher precedence than defaults)
  meta/main.yml         # Role metadata (author, description, deps)
  files/                # Static files to copy
  README.md             # Role documentation
```

**Key distinction**:
- `defaults/main.yml` — values the user CAN override (good for configurable defaults)
- `vars/main.yml` — values the role SETS (not meant to be overridden)

For this mission, put SSH settings and banner text in `defaults/main.yml` (so they can be overridden by group_vars or vault). Put things that should never change (like file paths) in `vars/main.yml` or directly in tasks.

### Step 1.3 — Run ARIA

```bash
cd ..
make test
cd workspace
```

---

## PHASE 2: Build the Role

> Create the role structure. Move tasks, handlers, and templates from your Mission 1.4 work into the role.

### Step 2.1 — Create the Role

```bash
ansible-galaxy init roles/fleet_hardening
```

This creates the full directory structure. Examine what was generated:

```bash
ls roles/fleet_hardening/
```

### Step 2.2 — Populate defaults/main.yml

Edit `roles/fleet_hardening/defaults/main.yml` with your SSH variables:

```yaml
---
ssh_permit_root_login: "no"
ssh_password_authentication: "no"
ssh_login_grace_time: 30
ssh_max_auth_tries: 3
ssh_service_name: ssh
banner_message: "STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY"
```

These are defaults — they can be overridden by `group_vars/` or the vault.

### Step 2.3 — Populate group_vars

Since the SSH service name and firewall differ by OS, ensure your group_vars override the defaults:

**inventory/group_vars/debian.yml:**
```yaml
---
ssh_service_name: ssh
firewall_pkg: ufw
```

**inventory/group_vars/redhat.yml:**
```yaml
---
ssh_service_name: sshd
firewall_pkg: firewalld
```

### Step 2.4 — Move Templates

Copy your Jinja2 templates from Mission 1.4 into the role:

```
roles/fleet_hardening/templates/sshd_config.j2
roles/fleet_hardening/templates/motd.j2
```

Create these templates following the same patterns from Mission 1.4. The templates use `{{ variable_name }}` to insert values.

### Step 2.5 — Write tasks/main.yml

This is where your hardening tasks go. Consolidate from Missions 1.2–1.4:

1. Deploy SSH configuration (template module)
2. Deploy MOTD (template module)
3. Install firewall (conditional apt/dnf)
4. Allow SSH through firewall (conditional ufw/firewalld)
5. Enable firewall (conditional)

Each task uses variables from `defaults/` or `group_vars/` — no hardcoded values.

### Step 2.6 — Write handlers/main.yml

Move your SSH restart handler here:

```yaml
---
- name: Restart SSH
  ansible.builtin.service:
    name: "{{ ssh_service_name }}"
    state: restarted
```

### Step 2.7 — Edit meta/main.yml

Update the metadata:

```yaml
---
galaxy_info:
  author: "Your Name"
  description: "Fleet hardening role — SSH, firewall, templates"
  license: MIT
  min_ansible_version: "2.14"
  platforms:
    - name: Ubuntu
      versions: ["22.04"]
    - name: EL
      versions: ["9"]
```

### Step 2.8 — Uncomment site.yml

Edit `workspace/site.yml` — uncomment the play that calls the role:

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

### Step 2.9 — Run ARIA

```bash
cd ..
make test
cd workspace
```

---

## PHASE 3: Crypto Cell (Vault)

> Encrypt sensitive values. Colonel Hardcoded-Password's reign ends here.

### Step 3.1 — Create a Vault Password File

The vault password file allows Ansible to decrypt vault files automatically. Create it:

```bash
echo 'starfall-academy-2187' > .vault-pass
chmod 600 .vault-pass
```

This file is **gitignored** — it never enters version control. The `ansible.cfg` already references it via `vault_password_file = .vault-pass`.

### Step 3.2 — Create the Vault File

```bash
ansible-vault create vault.yml
```

This opens an editor. Add your sensitive values:

```yaml
vault_ssh_login_grace_time: 30
vault_banner_message: "STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY"
```

Save and close. The file is now encrypted.

**Alternative — create then encrypt:**

```bash
# Create the file first:
cat > vault.yml << 'EOF'
vault_ssh_login_grace_time: 30
vault_banner_message: "STARFALL DEFENCE CORPS — AUTHORISED PERSONNEL ONLY"
EOF

# Then encrypt it:
ansible-vault encrypt vault.yml
```

### Step 3.3 — Reference Vault Variables

In your role's `defaults/main.yml`, you can reference vault variables:

```yaml
ssh_login_grace_time: "{{ vault_ssh_login_grace_time }}"
banner_message: "{{ vault_banner_message }}"
```

Or reference them directly in `site.yml`'s `vars_files`, which makes them available to the role.

### Step 3.4 — Verify Vault is Encrypted

```bash
cat vault.yml
```

You should see `$ANSIBLE_VAULT;1.1;AES256` followed by encrypted data. If you see plaintext, encrypt it:

```bash
ansible-vault encrypt vault.yml
```

### Step 3.5 — Verify No Plaintext Secrets

ARIA will scan your entire workspace for known sensitive values. Ensure the Colonel's credentials don't appear in any file (the vault file is excluded from this scan since it's encrypted).

### Step 3.6 — Run ARIA

```bash
cd ..
make test
cd workspace
```

---

## PHASE 4: Deploy & Verify

### Step 4.1 — Dry Run

```bash
ansible-playbook site.yml --check --diff
```

### Step 4.2 — Execute

```bash
ansible-playbook site.yml
```

### Step 4.3 — Verify

```bash
# SSH hardened?
ansible all -m shell -a "grep PermitRootLogin /etc/ssh/sshd_config"

# MOTD deployed?
ansible all -m shell -a "cat /etc/motd"
```

### Step 4.4 — Idempotency

```bash
ansible-playbook site.yml
```

`changed=0` on all hosts.

### Step 4.5 — Final ARIA Verification

```bash
cd ..
make test
```

---

## MISSION COMPLETE — DEBRIEF CHECKLIST

- [ ] Found Colonel Hardcoded-Password's plaintext credentials
- [ ] Created `fleet_hardening` role with `ansible-galaxy init`
- [ ] Populated role: tasks, handlers, templates, defaults, meta
- [ ] Created and encrypted `vault.yml`
- [ ] Created `.vault-pass` file (gitignored)
- [ ] No plaintext secrets in workspace
- [ ] `site.yml` calls the role with `vars_files: vault.yml`
- [ ] Role works on both Ubuntu and Rocky Linux
- [ ] Second run is idempotent
- [ ] `make test` — all ARIA checks pass

**What you learned in this mission:**

- [ ] Ansible role directory structure
- [ ] `ansible-galaxy init` for scaffolding
- [ ] `defaults/main.yml` vs `vars/main.yml` (precedence)
- [ ] Ansible Vault — the Crypto Cell
- [ ] `ansible-vault create/encrypt/decrypt/edit`
- [ ] Vault password files and `ansible.cfg` integration
- [ ] Why plaintext secrets in repos are dangerous
- [ ] Consolidating loose playbooks into reusable roles

**You are now ready for the Gateway Simulation.**

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
