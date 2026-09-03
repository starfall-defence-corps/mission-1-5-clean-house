"""
ARIA Custom Test Reporter
Provides color-coded, phase-grouped output for mission verification.

Writes all output to stderr so check-work.sh can discard pytest's
default stdout while preserving our formatted display.
"""
import os
import pytest
import sys

# -- Phase and test name mappings -------------------------------------------

PHASES = {
    "TestRoleStructure":     ("1", "Role Structure"),
    "TestVault":             ("2", "Crypto Cell (Vault)"),
    "TestRoleApplied":       ("3", "Role Deployment"),
    "TestIdempotency":       ("4", "Idempotency"),
}

FRIENDLY = {
    "test_role_directory_exists":        "Role directory exists",
    "test_tasks_main_exists":            "tasks/main.yml exists",
    "test_handlers_main_exists":         "handlers/main.yml exists",
    "test_templates_dir_exists":         "templates/ directory exists",
    "test_defaults_or_vars_exists":      "defaults/ or vars/ contains variables",
    "test_meta_main_exists":             "meta/main.yml exists",
    "test_vault_file_exists":            "vault.yml exists",
    "test_vault_file_encrypted":         "vault.yml is encrypted",
    "test_no_plaintext_secrets":         "No plaintext secrets in workspace",
    "test_vault_pass_file_exists":       ".vault-pass file exists",
    "test_site_yml_references_role":     "site.yml references fleet_hardening role",
    "test_ssh_hardened_all_nodes":        "SSH hardened on all nodes",
    "test_motd_deployed":                "Login banner deployed",
    "test_db_credential_secured":        "Rotated DB credential deployed root-only (0600)",
    "test_playbook_is_idempotent":       "Role is idempotent (changed=0)",
}

# -- Reporter ---------------------------------------------------------------

# The phase-oriented summary is rendered by the shared `aria-reporter`
# pytest plugin (installed via requirements.txt); this file only declares
# the mission's phases + friendly objective names.
from aria_reporter import configure  # noqa: E402

configure(phases=PHASES, friendly=FRIENDLY, mission_id="1-5")
