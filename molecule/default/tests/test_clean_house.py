"""
=== STARFALL DEFENCE CORPS ACADEMY ===
ARIA Automated Verification - Mission 1.5: Clean House
=======================================================
"""
import os
import re
import subprocess
import yaml
import pytest


def _root_dir():
    """Return the mission root directory."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(tests_dir, "..", "..", ".."))


def _workspace_dir():
    return os.path.join(_root_dir(), "workspace")


def _role_dir():
    return os.path.join(_workspace_dir(), "roles", "fleet_hardening")


def _run_ansible(*args, **kwargs):
    """Run an ansible command from the workspace directory."""
    timeout = kwargs.pop("timeout", 90)
    result = subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=_workspace_dir(),
    )
    return result


# -------------------------------------------------------------------
# Phase 1: Role structure
# -------------------------------------------------------------------

class TestRoleStructure:
    """ARIA verifies: Has the cadet built a proper role?"""

    def test_role_directory_exists(self):
        """Role directory must exist at workspace/roles/fleet_hardening/"""
        assert os.path.isdir(_role_dir()), (
            "ARIA: No role found at roles/fleet_hardening/. "
            "Create it with: ansible-galaxy init roles/fleet_hardening"
        )

    def test_tasks_main_exists(self):
        """Role must have tasks/main.yml"""
        path = os.path.join(_role_dir(), "tasks", "main.yml")
        if not os.path.isdir(_role_dir()):
            pytest.skip("Role directory does not exist yet")
        assert os.path.isfile(path), (
            "ARIA: tasks/main.yml not found in role. "
            "This is where your role's tasks are defined."
        )
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None and isinstance(data, list) and len(data) >= 1, (
            "ARIA: tasks/main.yml is empty. Transfer your hardening "
            "tasks from previous missions into this file."
        )

    def test_handlers_main_exists(self):
        """Role must have handlers/main.yml with at least one handler"""
        path = os.path.join(_role_dir(), "handlers", "main.yml")
        if not os.path.isdir(_role_dir()):
            pytest.skip("Role directory does not exist yet")
        assert os.path.isfile(path), (
            "ARIA: handlers/main.yml not found in role."
        )
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None and isinstance(data, list) and len(data) >= 1, (
            "ARIA: handlers/main.yml is empty. Move your SSH restart "
            "handler here."
        )

    def test_templates_dir_exists(self):
        """Role must have a templates/ directory with at least one template"""
        path = os.path.join(_role_dir(), "templates")
        if not os.path.isdir(_role_dir()):
            pytest.skip("Role directory does not exist yet")
        assert os.path.isdir(path), (
            "ARIA: templates/ directory not found in role."
        )
        templates = [f for f in os.listdir(path) if f.endswith(".j2")]
        assert len(templates) >= 1, (
            "ARIA: No .j2 templates found in templates/. "
            "Move your sshd_config.j2 and motd.j2 here."
        )

    def test_defaults_or_vars_exists(self):
        """Role must have defaults/main.yml or vars/main.yml with variables"""
        if not os.path.isdir(_role_dir()):
            pytest.skip("Role directory does not exist yet")
        defaults = os.path.join(_role_dir(), "defaults", "main.yml")
        role_vars = os.path.join(_role_dir(), "vars", "main.yml")
        has_defaults = False
        has_vars = False
        if os.path.isfile(defaults):
            with open(defaults) as f:
                data = yaml.safe_load(f)
            if data and isinstance(data, dict) and len(data) >= 1:
                has_defaults = True
        if os.path.isfile(role_vars):
            with open(role_vars) as f:
                data = yaml.safe_load(f)
            if data and isinstance(data, dict) and len(data) >= 1:
                has_vars = True
        assert has_defaults or has_vars, (
            "ARIA: Neither defaults/main.yml nor vars/main.yml contains "
            "variable definitions. Define your role's default values."
        )

    def test_meta_main_exists(self):
        """Role must have meta/main.yml"""
        path = os.path.join(_role_dir(), "meta", "main.yml")
        if not os.path.isdir(_role_dir()):
            pytest.skip("Role directory does not exist yet")
        assert os.path.isfile(path), (
            "ARIA: meta/main.yml not found. This file describes "
            "role metadata (author, description, dependencies)."
        )


# -------------------------------------------------------------------
# Phase 2: Vault
# -------------------------------------------------------------------

class TestVault:
    """ARIA verifies: Are secrets properly vaulted?"""

    def test_vault_file_exists(self):
        """vault.yml must exist in workspace/"""
        path = os.path.join(_workspace_dir(), "vault.yml")
        assert os.path.isfile(path), (
            "ARIA: vault.yml not found in workspace/. "
            "Create it with: ansible-vault create vault.yml"
        )

    def test_vault_file_encrypted(self):
        """vault.yml must be encrypted (not plaintext)"""
        path = os.path.join(_workspace_dir(), "vault.yml")
        if not os.path.isfile(path):
            pytest.skip("vault.yml does not exist yet")
        with open(path) as f:
            first_line = f.readline().strip()
        assert first_line.startswith("$ANSIBLE_VAULT;"), (
            "ARIA: vault.yml is NOT encrypted. Colonel Hardcoded-Password "
            "would approve of your plaintext secrets. Encrypt it with: "
            "ansible-vault encrypt vault.yml"
        )

    def test_no_plaintext_secrets(self):
        """No plaintext passwords or API keys in workspace files"""
        sensitive_patterns = [
            "V01dborn_Hunter_2187",
            "sk-sdc-1a2b3c4d5e6f7g8h9i0j",
            "fleet_db_pass",
            "fleet_api_key",
        ]
        violations = []
        for root, dirs, files in os.walk(_workspace_dir()):
            # Skip .ssh directory and __pycache__
            dirs[:] = [d for d in dirs if d not in (".ssh", "__pycache__", ".git")]
            for fname in files:
                fpath = os.path.join(root, fname)
                if fname.endswith((".pyc", ".key")):
                    continue
                try:
                    with open(fpath) as f:
                        content = f.read()
                except (UnicodeDecodeError, PermissionError):
                    continue
                # Skip encrypted vault files
                if content.startswith("$ANSIBLE_VAULT;"):
                    continue
                for pattern in sensitive_patterns:
                    if pattern in content:
                        rel = os.path.relpath(fpath, _workspace_dir())
                        violations.append(f"{rel} contains '{pattern}'")
        assert not violations, (
            f"ARIA: Plaintext secrets detected! Colonel Hardcoded-Password "
            f"lives on in your files:\n"
            + "\n".join(f"  - {v}" for v in violations)
            + "\nEncrypt sensitive values in vault.yml."
        )

    def test_vault_pass_file_exists(self):
        """.vault-pass file must exist (for automated decryption)"""
        path = os.path.join(_workspace_dir(), ".vault-pass")
        assert os.path.isfile(path), (
            "ARIA: .vault-pass file not found. Create it with your vault "
            "password so ansible-playbook can decrypt vault.yml automatically. "
            "This file is gitignored — it never enters version control."
        )


# -------------------------------------------------------------------
# Phase 3: Role deployment
# -------------------------------------------------------------------

class TestRoleApplied:
    """ARIA verifies: Does the role work?"""

    @pytest.fixture(autouse=True)
    def _require_role(self):
        if not os.path.isdir(_role_dir()):
            pytest.skip("Role does not exist yet")
        tasks = os.path.join(_role_dir(), "tasks", "main.yml")
        if not os.path.isfile(tasks):
            pytest.skip("Role tasks not yet written")

    def test_site_yml_references_role(self):
        """site.yml must reference the fleet_hardening role"""
        path = os.path.join(_workspace_dir(), "site.yml")
        assert os.path.isfile(path), (
            "ARIA: site.yml not found in workspace/."
        )
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None and isinstance(data, list), (
            "ARIA: site.yml is empty or commented out. "
            "Uncomment the play that calls the fleet_hardening role."
        )
        play = data[0]
        roles = play.get("roles") or []
        role_names = []
        for r in roles:
            if isinstance(r, str):
                role_names.append(r)
            elif isinstance(r, dict):
                role_names.append(r.get("role", r.get("name", "")))
        assert "fleet_hardening" in role_names, (
            "ARIA: site.yml does not reference the fleet_hardening role. "
            "Add it to the roles list."
        )

    def test_ssh_hardened_all_nodes(self):
        """SSH must be hardened on all nodes via the role"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "grep -E '^PermitRootLogin\\s+no' /etc/ssh/sshd_config",
        )
        assert result.returncode == 0, (
            "ARIA: SSH is not hardened on all nodes. "
            "Run: ansible-playbook site.yml"
        )

    def test_motd_deployed(self):
        """Login banner must be deployed on all nodes"""
        result = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "cat /etc/motd",
        )
        assert result.returncode == 0 and "STARFALL" in result.stdout, (
            "ARIA: Login banner not deployed. Ensure the role "
            "deploys a MOTD template."
        )


# -------------------------------------------------------------------
# Phase 4: Idempotency
# -------------------------------------------------------------------

class TestIdempotency:
    """ARIA verifies: Is the role idempotent?"""

    def test_playbook_is_idempotent(self):
        """Running site.yml must show changed=0"""
        if not os.path.isdir(_role_dir()):
            pytest.skip("Role does not exist yet")

        # Check if hardening has been applied
        check = _run_ansible(
            "ansible", "all", "-m", "shell",
            "-a", "grep -E '^PermitRootLogin\\s+no' /etc/ssh/sshd_config",
        )
        if check.returncode != 0:
            pytest.skip("Fleet not yet hardened — run site.yml first")

        result = _run_ansible(
            "ansible-playbook", "site.yml",
            timeout=120,
        )
        assert result.returncode == 0, (
            "ARIA: site.yml failed. Fix errors and try again."
        )
        changed_match = re.findall(r"changed=(\d+)", result.stdout)
        total_changed = sum(int(c) for c in changed_match)
        assert total_changed == 0, (
            f"ARIA: Idempotency failure. Role changed "
            f"{total_changed} task(s). A proper SOP produces the same "
            f"result every time."
        )
