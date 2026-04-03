# Starfall Defence Corps Academy

## Mission 1.5: Clean House

> *"Colonel Hardcoded-Password embedded database credentials in three public repos. Plaintext. In the commit history. This ends now."*

You are a cadet at the Starfall Defence Corps Academy. Everything you've built in Missions 1.2–1.4 — SSH hardening, service cleanup, multi-OS support — exists as loose playbooks. Colonel Hardcoded-Password has proven what happens when secrets aren't managed properly. Your mission: restructure everything into a proper Ansible role, encrypt secrets with Vault, and follow Git workflow discipline.

This is the final mission before the Gateway Simulation.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with Docker Compose v2)
- [GNU Make](https://www.gnu.org/software/make/)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/) (`ansible-core`)
- Python 3.10+ (for test environment)
  - On Debian/Ubuntu: `sudo apt install python3-venv`
- Git

> **Windows users**: Install [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) and run all commands from within your WSL terminal.

## Quick Start

```bash
# 1. Use this template on GitHub (green button, top right)
git clone https://github.com/YOUR-USERNAME/mission-1-5-clean-house.git
cd mission-1-5-clean-house

# 2. Start the fleet
make setup

# 3. Activate the virtual environment
source venv/bin/activate
```

4. **Read your orders**: [Mission Briefing](docs/BRIEFING.md)
5. **Complete the exercises**: [Exercises](docs/EXERCISES.md)
6. **Stuck?** [Hints & Troubleshooting](docs/HINTS.md)
7. **Track progress**: [Checklist](CHECKLIST.md)

## Lab Architecture

```
 Your Machine
+--------------------------------------------------+
|  workspace/                                      |
|    ansible.cfg          (pre-configured)         |
|    inventory/           (pre-configured)         |
|    site.yml             (you uncomment)          |
|    vault.yml            (you create + encrypt)   |
|    .vault-pass          (you create, gitignored) |
|    roles/                                        |
|      fleet_hardening/   (you create via galaxy)  |
|        tasks/main.yml                            |
|        handlers/main.yml                         |
|        templates/                                |
|        defaults/main.yml                         |
|                                                  |
|  Docker Network: 172.30.0.0/24                   |
|  +------------+ +-------------+ +------------+  |
|  | sdc-web    | | sdc-db      | | sdc-comms  |  |
|  | :2221      | | :2222       | | :2223      |  |
|  | Ubuntu22.04| | Rocky Lin 9 | | Ubuntu22.04|  |
|  | Colonel's plaintext creds on each node    |  |
|  +------------+ +-------------+ +------------+  |
+--------------------------------------------------+
```

## Available Commands

```
make help       Show available commands
make setup      Start the fleet (2 Ubuntu + 1 Rocky Linux)
make test       Ask ARIA to verify your work
make reset      Destroy and rebuild all fleet nodes
make destroy    Tear down everything (containers, keys, venv)
make ssh-web    SSH into sdc-web (Ubuntu)
make ssh-db     SSH into sdc-db (Rocky Linux)
make ssh-comms  SSH into sdc-comms (Ubuntu)
```

## Mission Files

| File | Purpose |
|------|---------|
| [BRIEFING.md](docs/BRIEFING.md) | Mission briefing — **read this first** |
| [EXERCISES.md](docs/EXERCISES.md) | Step-by-step exercises (4 phases) |
| [HINTS.md](docs/HINTS.md) | Troubleshooting and hints |
| [CHECKLIST.md](CHECKLIST.md) | Progress tracker |

## ARIA Review (Pull Request Workflow)

**Locally** — run `make test` for instant verification.

**On Pull Request** — push your work, open a PR, ARIA reviews automatically.

To enable PR reviews, add `ANTHROPIC_API_KEY` to your repo's Secrets (Settings > Secrets > Actions).

## Troubleshooting

**"Decryption failed"**: Your `.vault-pass` doesn't match the password used to encrypt `vault.yml`. Re-create one or the other.

**"the role 'fleet_hardening' was not found"**: Ensure the role is at `workspace/roles/fleet_hardening/` and `ansible.cfg` has `roles_path = roles`.

**Need a clean slate**: Run `make reset` to destroy and rebuild containers. Your workspace files are preserved.
