"""
ARIA Custom Test Reporter
Provides color-coded, phase-grouped output for mission verification.

Writes all output to stderr so check-work.sh can discard pytest's
default stdout while preserving our formatted display.
"""
import os
import pytest
import sys

# -- ANSI escape codes ------------------------------------------------------

_COLOR = (
    os.environ.get("ARIA_COLOR") == "1"
    or (hasattr(sys.stderr, "isatty") and sys.stderr.isatty())
)


def _c(code):
    return code if _COLOR else ""


GREEN = _c("\033[32m")
RED = _c("\033[31m")
YELLOW = _c("\033[33m")
CYAN = _c("\033[36m")
DIM = _c("\033[2m")
BOLD = _c("\033[1m")
RESET = _c("\033[0m")

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
    "test_playbook_is_idempotent":       "Role is idempotent (changed=0)",
}

# -- Reporter ---------------------------------------------------------------


class _ARIAReporter:
    def __init__(self):
        self._current_class = None
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self._phase_results = {}
        self._current_phase_passed = True

    @staticmethod
    def _out(text):
        sys.stderr.write(text)
        sys.stderr.flush()

    def record(self, nodeid, outcome, longrepr):
        parts = nodeid.split("::")
        cls = parts[1] if len(parts) > 1 else ""
        test = parts[-1]

        num, label = PHASES.get(cls, ("?", "Unknown"))
        name = FRIENDLY.get(test, test)

        if cls != self._current_class:
            if self._current_class is not None:
                self._phase_results[self._current_class] = self._current_phase_passed
            self._current_phase_passed = True
            self._current_class = cls
            self._out(f"\n  {CYAN}{BOLD}Phase {num}: {label}{RESET}\n")

        if outcome != "passed":
            self._current_phase_passed = False

        if outcome == "passed":
            self.passed += 1
            self._out(f"    {GREEN}\u2713{RESET} {name}\n")
        elif outcome == "skipped":
            self.skipped += 1
            self._out(f"    {YELLOW}\u25cb{RESET} {DIM}{name} \u2014 skipped{RESET}\n")
        else:
            self.failed += 1
            hint = _extract_hint(longrepr)
            if hint:
                self._out(f"    {YELLOW}\u2717{RESET} {name}\n")
                self._out(f"      {DIM}\u21b3 {hint}{RESET}\n")
            else:
                self._out(f"    {RED}\u2717{RESET} {name}\n")

    def summary(self):
        if self._current_class is not None:
            self._phase_results[self._current_class] = self._current_phase_passed

        total = self.passed + self.failed + self.skipped
        self._out(f"\n  {'\u2500' * 44}\n")

        phases_complete = sum(1 for v in self._phase_results.values() if v)
        total_phases = len(PHASES)
        self._out(f"  {BOLD}Progress:{RESET} {phases_complete} of {total_phases} phases complete\n")

        parts = []
        if self.passed:
            parts.append(f"{GREEN}{self.passed} verified{RESET}")
        if self.failed:
            parts.append(f"{RED}{self.failed} deficient{RESET}")
        if self.skipped:
            parts.append(f"{YELLOW}{self.skipped} skipped{RESET}")
        self._out(
            f"  {BOLD}Results:{RESET} {' \u00b7 '.join(parts)}"
            f"  {DIM}({total} checks){RESET}\n"
        )


def _extract_hint(longrepr):
    """Pull the ARIA: message from an assertion failure."""
    if longrepr is None:
        return None
    crash = getattr(longrepr, "reprcrash", None)
    if crash:
        msg = getattr(crash, "message", "")
        if "ARIA:" in msg:
            return msg.split("ARIA:", 1)[-1].strip()
    text = str(longrepr)
    if "ARIA:" in text:
        raw = text.split("ARIA:")[-1].splitlines()[0].strip()
        return raw.rstrip("'\"")
    return None


# -- Singleton instance -----------------------------------------------------

_reporter = _ARIAReporter()

# -- Pytest hooks -----------------------------------------------------------


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    """Intercept results before the default reporter sees them."""
    if report.when == "call":
        _reporter.record(report.nodeid, report.outcome, report.longrepr)
        report.longrepr = None
    elif report.when == "setup" and report.skipped:
        _reporter.record(report.nodeid, "skipped", report.longrepr)
        report.longrepr = None


def pytest_report_teststatus(report, config):
    """Return empty strings so the default reporter prints nothing per-test."""
    if report.when == "call":
        return report.outcome, "", ""
    if report.when == "setup" and report.skipped:
        return "skipped", "", ""


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print our summary; clear stats to suppress the default summary."""
    _reporter.summary()
    terminalreporter.stats.pop("failed", None)
    terminalreporter.stats.pop("error", None)
