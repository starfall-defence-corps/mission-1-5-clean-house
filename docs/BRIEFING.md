---
CLASSIFICATION: CADET EYES ONLY
MISSION: 1.5 — CLEAN HOUSE
THEATRE: Starfall Defence Corps Academy
AUTHORITY: SDC Cyber Command, 2187
---

# OPERATION ORDER — MISSION 1.5: CLEAN HOUSE

---

## 1. SITUATION

### 1a. Enemy Forces

Voidborn operative **COLONEL HARDCODED-PASSWORD** has embedded database credentials in three fleet systems. Plaintext. On the filesystem. The Colonel's philosophy: "If it works, why encrypt it?" Because the Voidborn read files too, Colonel.

Evidence of the Colonel's work is present on every fleet node at `/opt/fleet-db-creds.txt`. Examine it. Then ensure nothing like it ever happens again.

### 1b. Friendly Forces

Over the past four missions, you have built:
- An inventory of fleet assets (1.1)
- SSH hardening via playbook (1.2)
- Service cleanup and firewall configuration (1.3)
- Multi-OS support via variables and templates (1.4)

But this work exists as loose playbooks. No structure. No reusability. No secret management. It is time to turn ad-hoc solutions into **Standard Operating Procedures** — Ansible roles.

### 1c. Attachments / Support

**ARIA** verifies role structure, Vault encryption, and deployment compliance. She is particularly vigilant about plaintext secrets.

### 1d. Operational Tools

| Tool | Purpose |
|------|---------|
| `ansible-galaxy init` | Generate role directory structure |
| `ansible-vault` | Encrypt/decrypt sensitive data — the **Crypto Cell** |
| Git workflow | Branch → commit → PR — change authorisation |

---

## 2. MISSION

Restructure your hardening work from Missions 1.2–1.4 into a proper Ansible role. Store all sensitive values in Ansible Vault. Follow Git workflow discipline.

**End state**: A `fleet_hardening` role that hardens SSH, deploys templates, and manages the firewall on both OS families. Sensitive values encrypted in Vault. No plaintext secrets anywhere in the workspace.

---

## 3. EXECUTION

### 3a. Commander's Intent

Loose playbooks are prototypes. Roles are production-ready SOPs. The fleet depends on hardening that is repeatable, auditable, and secure. Colonel Hardcoded-Password proved what happens when secrets are treated casually. This mission closes that gap.

### 3b. Concept of Operations

Four sequential phases.

| Phase | Task | Objective |
|-------|------|-----------|
| 1 | Intelligence Gathering | Find the Colonel's secrets, understand role structure |
| 2 | Build the Role | Create `fleet_hardening` role, move tasks and templates |
| 3 | Crypto Cell (Vault) | Encrypt sensitive values, reference from role |
| 4 | Deploy & Verify | Run `site.yml`, confirm idempotency |

### 3c. Fleet Assets

Same mixed-OS fleet as Mission 1.4.

| Designation | OS | SSH Port |
|-------------|----|----------|
| `sdc-web` | Ubuntu 22.04 | 2221 |
| `sdc-db` | Rocky Linux 9 | 2222 |
| `sdc-comms` | Ubuntu 22.04 | 2223 |

### 3d. Rules of Engagement

- **No skeleton playbook**. You create the role yourself with `ansible-galaxy init`.
- All sensitive values must be in Vault — no plaintext passwords or keys.
- The site playbook (`site.yml`) calls the role. No inline tasks in `site.yml`.
- `.vault-pass` is gitignored. It never enters version control.

---

## 4. SUPPORT

| Resource | Function | Command |
|----------|----------|---------|
| **ARIA** | Verifies role structure and vault compliance | `make test` |
| **HINTS.md** | Operational guidance | — |
| **Fleet Reset** | Rebuild containers | `make reset` |
| **Galaxy Docs** | Role structure reference | `ansible-galaxy init --help` |
| **Vault Docs** | Vault command reference | `ansible-vault --help` |

---

## 5. COMMAND AND SIGNAL

**Commander's Final Order**: Colonel Hardcoded-Password's legacy ends with this mission. Every secret encrypted. Every playbook structured as a reusable role. Every change through proper authorisation. When you complete this mission, you will have earned every skill needed for the Gateway Simulation. Clean house. Leave nothing for the Voidborn.

Proceed to **EXERCISES.md** for phase-by-phase operational instructions.

---

*SDC Cyber Command — 2187 — CADET EYES ONLY*
