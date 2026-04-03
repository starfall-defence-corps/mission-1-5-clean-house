# Mission 1.5: Clean House — Progress Tracker

**Rank**: Ensign Candidate
**Mission Progress**: 5 of 5 toward Ensign

---

## Phase 1: Intelligence Gathering

- [ ] Fleet nodes are online (`make setup` succeeded)
- [ ] Found Colonel Hardcoded-Password's plaintext credentials at `/opt/fleet-db-creds.txt`
- [ ] Understand Ansible role directory structure
- [ ] Understand the difference between `defaults/` and `vars/`

---

## Phase 2: Build the Role

- [ ] Created role with `ansible-galaxy init roles/fleet_hardening`
- [ ] Populated `defaults/main.yml` with SSH variables
- [ ] Populated `group_vars/debian.yml` and `group_vars/redhat.yml`
- [ ] Created templates: `sshd_config.j2` and `motd.j2`
- [ ] Wrote `tasks/main.yml` — SSH, MOTD, firewall (both OS families)
- [ ] Wrote `handlers/main.yml` — SSH restart handler
- [ ] Updated `meta/main.yml` with role metadata
- [ ] Uncommented `site.yml` to call the role

---

## Phase 3: Crypto Cell (Vault)

- [ ] Created `.vault-pass` with vault password
- [ ] Created `vault.yml` with sensitive values
- [ ] Encrypted `vault.yml` with `ansible-vault encrypt`
- [ ] Verified: `cat vault.yml` shows `$ANSIBLE_VAULT;` header
- [ ] No plaintext secrets anywhere in workspace
- [ ] `site.yml` includes `vars_files: vault.yml`

---

## Phase 4: Deploy & Verify

- [ ] Dry run succeeded (`ansible-playbook site.yml --check --diff`)
- [ ] Role executed successfully on all nodes
- [ ] SSH hardened on Ubuntu and Rocky Linux
- [ ] MOTD deployed with host-specific content
- [ ] Firewall active on both OS families
- [ ] Second run is idempotent — `changed=0` on all hosts
- [ ] `make test` — all ARIA checks pass

---

## Verification

- [ ] `make test` — all ARIA checks pass
- [ ] Ready for Gateway Simulation
