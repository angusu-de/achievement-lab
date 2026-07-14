#!/usr/bin/env python3
"""Run transparent GitHub achievement experiments in one isolated repository."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

VERSION = "1.4.0"
PREFIX = "[ALAB"
SUPPORTED = ("quickdraw", "yolo", "pull-shark", "pair-extraordinaire")

ACHIEVEMENTS: tuple[dict[str, Any], ...] = (
    {
        "name": "Pull Shark",
        "status": "observed",
        "tiers": (2, 16, 128, 1024),
        "route": "Author useful pull requests that get merged.",
        "automation": "guarded",
    },
    {
        "name": "Galaxy Brain",
        "status": "observed",
        "tiers": (2, 8, 16, 32),
        "route": "Give answers in Discussions that the question author accepts.",
        "automation": "manual",
    },
    {
        "name": "Pair Extraordinaire",
        "status": "observed",
        "tiers": (10, 24, 48, 64),
        "route": "Ship genuine commits credited to multiple authors.",
        "automation": "guarded",
    },
    {
        "name": "Starstruck",
        "status": "observed-social",
        "tiers": (16, 128, 512, 4096),
        "route": "Build repositories people voluntarily choose to star.",
        "automation": "never",
    },
    {
        "name": "Quickdraw",
        "status": "observed",
        "tiers": (),
        "route": "Close an issue shortly after opening it.",
        "automation": "guarded",
    },
    {
        "name": "Public Sponsor",
        "status": "active-social",
        "tiers": (),
        "route": "Publicly sponsor open-source work through GitHub Sponsors.",
        "automation": "never",
    },
)


class LabError(RuntimeError):
    """Expected user-facing error."""


@dataclass(frozen=True)
class Config:
    target_login: str
    helper_login: str
    evidence_repo: str = "achievement-lab-private"
    visibility: str = "private"
    default_branch: str = "main"
    delay_seconds: float = 1.0
    safe_batch_limit: int = 16

    @property
    def full_repo(self) -> str:
        return f"{self.target_login}/{self.evidence_repo}"

    def validate(self) -> None:
        if "achievement-lab" not in self.evidence_repo.casefold():
            raise LabError("Refusing writes: evidence_repo must contain 'achievement-lab'.")
        if self.target_login.casefold() == self.helper_login.casefold():
            raise LabError("Target and helper accounts must be different.")
        if self.visibility not in {"private", "public"}:
            raise LabError("visibility must be 'private' or 'public'.")
        if self.safe_batch_limit < 1:
            raise LabError("safe_batch_limit must be positive.")


class Gh:
    def __init__(self, login: str) -> None:
        self.login = login

    def run(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        fields: dict[str, Any] | None = None,
        paginate: bool = False,
    ) -> Any:
        command = ["gh", "api", endpoint, "--method", method]
        if paginate:
            command += ["--paginate", "--slurp"]
        payload = json.dumps(fields) if fields is not None else None
        if payload is not None:
            command += ["--input", "-"]
        token = subprocess.run(
            ["gh", "auth", "token", "--hostname", "github.com", "--user", self.login],
            check=False,
            capture_output=True,
            text=True,
        )
        if token.returncode != 0 or not token.stdout.strip():
            raise LabError(f"No GitHub CLI credential found for {self.login}.")
        result = subprocess.run(
            command,
            input=payload,
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "GH_TOKEN": token.stdout.strip()},
        )
        if result.returncode != 0:
            raise LabError(result.stderr.strip() or f"GitHub request failed: {endpoint}")
        if not result.stdout.strip():
            return {}
        return json.loads(result.stdout)

    def maybe(self, endpoint: str) -> Any | None:
        try:
            return self.run(endpoint)
        except LabError as exc:
            if "HTTP 404" in str(exc) or '"status":"404"' in str(exc).replace(" ", ""):
                return None
            raise


class Lab:
    def __init__(self, config: Config, *, dry_run: bool = False) -> None:
        config.validate()
        self.config = config
        self.target = Gh(config.target_login)
        self.helper = Gh(config.helper_login)
        self.dry_run = dry_run

    def pause(self) -> None:
        if self.config.delay_seconds > 0:
            time.sleep(self.config.delay_seconds)

    def doctor(self) -> None:
        if shutil.which("gh") is None:
            raise LabError("GitHub CLI is not installed.")
        target = self.target.run("user")
        helper = self.helper.run("user")
        if target.get("login", "").casefold() != self.config.target_login.casefold():
            raise LabError("Target credential does not match target_login.")
        if helper.get("login", "").casefold() != self.config.helper_login.casefold():
            raise LabError("Helper credential does not match helper_login.")
        print(f"OK target: @{target['login']}")
        print(f"OK helper: @{helper['login']}")
        repo = self.target.maybe(f"repos/{self.config.full_repo}")
        print(f"Evidence repository: {'ready' if repo else 'not created'} ({self.config.visibility})")
        print("Profile repository writes: not implemented")

    def init(self) -> None:
        if self.dry_run:
            print(f"DRY RUN create {self.config.visibility} repository {self.config.full_repo}")
            print(f"DRY RUN invite @{self.config.helper_login} with push permission")
            return
        repo = self.target.maybe(f"repos/{self.config.full_repo}")
        if repo is None:
            self.target.run(
                "user/repos",
                method="POST",
                fields={
                    "name": self.config.evidence_repo,
                    "description": "Private evidence for controlled GitHub achievement experiments.",
                    "private": self.config.visibility == "private",
                    "auto_init": True,
                    "has_issues": True,
                },
            )
        for name, color in {
            "achievement-lab": "7c5cfc",
            "quickdraw": "15d1c5",
            "yolo": "ff5c7c",
            "pull-shark": "58a6ff",
        }.items():
            existing = self.target.maybe(f"repos/{self.config.full_repo}/labels/{quote(name)}")
            if existing is None:
                try:
                    self.target.run(
                        f"repos/{self.config.full_repo}/labels",
                        method="POST",
                        fields={"name": name, "color": color, "description": "Controlled ALAB evidence"},
                    )
                except LabError as exc:
                    if "already_exists" not in str(exc):
                        raise
        self.target.run(
            f"repos/{self.config.full_repo}/collaborators/{self.config.helper_login}",
            method="PUT",
            fields={"permission": "push"},
        )
        invitations = self.helper.run("user/repository_invitations?per_page=100")
        for invitation in invitations:
            if invitation.get("repository", {}).get("full_name", "").casefold() == self.config.full_repo.casefold():
                self.helper.run(f"user/repository_invitations/{invitation['id']}", method="PATCH")
                break
        print(f"Ready: https://github.com/{self.config.full_repo}")

    def create_file(self, path: str, content: str, message: str, branch: str) -> None:
        self.target.run(
            f"repos/{self.config.full_repo}/contents/{quote(path, safe='/')}",
            method="PUT",
            fields={
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch,
            },
        )

    def create_pr(self, kind: str, merge_client: Gh) -> None:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        branch = f"alab/{kind}-{stamp}"
        ref = self.target.run(f"repos/{self.config.full_repo}/git/ref/heads/{self.config.default_branch}")
        self.target.run(
            f"repos/{self.config.full_repo}/git/refs",
            method="POST",
            fields={"ref": f"refs/heads/{branch}", "sha": ref["object"]["sha"]},
        )
        self.create_file(
            f"evidence/{kind}/{stamp}.md",
            f"# {kind}\n\nControlled Achievement Lab evidence.\n",
            f"[ALAB {kind}] add controlled evidence {stamp}",
            branch,
        )
        pr = self.target.run(
            f"repos/{self.config.full_repo}/pulls",
            method="POST",
            fields={
                "title": f"[ALAB {kind}] Controlled merge {stamp}",
                "head": branch,
                "base": self.config.default_branch,
                "body": "Transparent, isolated Achievement Lab evidence.",
            },
        )
        self.pause()
        merged = merge_client.run(
            f"repos/{self.config.full_repo}/pulls/{pr['number']}/merge",
            method="PUT",
            fields={"merge_method": "merge", "commit_title": f"[ALAB {kind}] merge #{pr['number']}"},
        )
        if not merged.get("merged"):
            raise LabError(f"PR #{pr['number']} was not merged: {merged}")
        print(f"Created and merged PR #{pr['number']} as {kind}")

    def quickdraw(self) -> None:
        issue = self.target.run(
            f"repos/{self.config.full_repo}/issues",
            method="POST",
            fields={
                "title": f"[ALAB quickdraw] Controlled close {utc_stamp()}",
                "body": "This controlled evidence issue is intentionally closed immediately.",
                "labels": ["achievement-lab", "quickdraw"],
            },
        )
        self.target.run(
            f"repos/{self.config.full_repo}/issues/{issue['number']}",
            method="PATCH",
            fields={"state": "closed", "state_reason": "completed"},
        )
        print(f"Created and closed issue #{issue['number']}")

    def pair(self) -> None:
        helper = self.helper.run("user")
        email = f"{helper['id']}+{self.config.helper_login}@users.noreply.github.com"
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        message = (
            f"[ALAB pair-extraordinaire] controlled co-author {stamp}\n\n"
            f"Co-authored-by: {helper.get('name') or self.config.helper_login} <{email}>"
        )
        self.create_file(
            f"evidence/pair-extraordinaire/{stamp}.md",
            "# Pair Extraordinaire\n\nControlled Achievement Lab evidence.\n",
            message,
            self.config.default_branch,
        )
        print("Created one co-authored commit")

    def add(self, scenario: str, count: int) -> None:
        if count < 1 or count > self.config.safe_batch_limit:
            raise LabError(f"count must be between 1 and {self.config.safe_batch_limit}.")
        if self.dry_run:
            print(f"DRY RUN add {count} x {scenario} to {self.config.full_repo}")
            return
        if self.target.maybe(f"repos/{self.config.full_repo}") is None:
            raise LabError("Evidence repository does not exist. Run init first.")
        for _ in range(count):
            if scenario == "quickdraw":
                self.quickdraw()
            elif scenario == "yolo":
                self.create_pr("yolo", self.target)
            elif scenario == "pull-shark":
                self.create_pr("pull-shark", self.helper)
            elif scenario == "pair-extraordinaire":
                self.pair()
            self.pause()

    def status(self) -> None:
        repo = self.target.maybe(f"repos/{self.config.full_repo}")
        if repo is None:
            print("Evidence repository not created.")
            return
        issues = self.target.run(f"repos/{self.config.full_repo}/issues?state=all&per_page=100")
        pulls = self.target.run(f"repos/{self.config.full_repo}/pulls?state=all&per_page=100")
        commits = self.target.run(f"repos/{self.config.full_repo}/commits?per_page=100")
        print(json.dumps({
            "repository": self.config.full_repo,
            "visibility": repo.get("visibility"),
            "quickdraw_issues": sum(1 for item in issues if item.get("title", "").startswith("[ALAB quickdraw]")),
            "merged_prs": sum(1 for item in pulls if item.get("merged_at")),
            "pair_commits": sum(1 for item in commits if item.get("commit", {}).get("message", "").startswith("[ALAB pair-extraordinaire]")),
        }, indent=2))


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_config(path: Path) -> Config:
    try:
        raw = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise LabError(f"Could not read config: {exc}") from exc
    missing = [key for key in ("target_login", "helper_login") if not raw.get(key)]
    if missing:
        raise LabError(f"Missing config fields: {', '.join(missing)}")
    return Config(**{key: value for key, value in raw.items() if key in Config.__dataclass_fields__})


def confirm(message: str, *, yes: bool, dry_run: bool) -> None:
    print(message)
    if dry_run:
        return
    if not yes and input("Continue? [y/N] ").strip().casefold() not in {"y", "yes"}:
        raise LabError("Cancelled.")


class Ui:
    """Small dependency-free terminal UI that stays readable without color."""

    def __init__(self) -> None:
        self.color = sys.stdout.isatty() and os.getenv("NO_COLOR") is None

    def paint(self, code: str, value: str) -> str:
        return f"\033[{code}m{value}\033[0m" if self.color else value

    def banner(self) -> None:
        print()
        print(self.paint("1;38;5;57", "  ACHIEVEMENT LAB"))
        print(self.paint("38;5;244", "  Clear profile choices. Controlled experiments."))
        print()

    def step(self, number: int, title: str, detail: str = "") -> None:
        print(f"{self.paint('1;38;5;57', f'{number:02d}')}  {self.paint('1', title)}")
        if detail:
            print(f"    {self.paint('38;5;244', detail)}")

    def note(self, value: str) -> None:
        print(self.paint("38;5;244", f"    {value}"))

    def success(self, value: str) -> None:
        print(self.paint("1;32", f"✓ {value}"))


def ask(prompt: str, *, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def choose(prompt: str, options: list[tuple[str, str]], *, default: int = 1) -> int:
    print(prompt)
    for index, (label, detail) in enumerate(options, start=1):
        print(f"  {index}. {label}")
        if detail:
            print(f"     {detail}")
    while True:
        raw = input(f"Choose [{default}]: ").strip() or str(default)
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw)
        print(f"Enter a number from 1 to {len(options)}.")


def connected_accounts() -> list[str]:
    """Return healthy GitHub CLI accounts without exposing their tokens."""
    if shutil.which("gh") is None:
        return []
    result = subprocess.run(
        ["gh", "auth", "status", "--hostname", "github.com", "--json", "hosts"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        hosts = json.loads(result.stdout).get("hosts", {})
    except json.JSONDecodeError:
        return []
    accounts = hosts.get("github.com", [])
    return [
        str(account["login"])
        for account in accounts
        if account.get("state") == "success" and account.get("login")
    ]


def connect_github() -> list[str]:
    ui = Ui()
    ui.banner()
    if shutil.which("gh") is None:
        raise LabError("GitHub CLI is required. Install it from https://cli.github.com/ first.")
    before = connected_accounts()
    if before:
        ui.success("Connected: " + ", ".join(f"@{login}" for login in before))
        selected = choose("GitHub connection", [
            ("Keep these accounts", "Return without changing authentication."),
            ("Connect another account", "Open GitHub's official browser/device login."),
        ])
        if selected == 1:
            return before
    else:
        print("No working GitHub CLI account was found.\n")
        selected = choose("Connect now?", [
            ("Connect with GitHub", "Uses GitHub's official browser/device flow."),
            ("Not now", "Return without changing authentication."),
        ])
        if selected == 2:
            return []
    print("\nGitHub will show a one-time code. No token is copied into Achievement Lab.\n")
    result = subprocess.run(
        ["gh", "auth", "login", "--hostname", "github.com", "--web", "--git-protocol", "https"],
        check=False,
    )
    if result.returncode != 0:
        raise LabError("GitHub login did not complete. No lab action was run.")
    after = connected_accounts()
    if not after:
        raise LabError("GitHub CLI still reports no connected account.")
    ui.success("Connected: " + ", ".join(f"@{login}" for login in after))
    return after


def choose_account(label: str, accounts: list[str], *, exclude: str = "") -> str:
    available = [login for login in accounts if login.casefold() != exclude.casefold()]
    if not available:
        return ask(label)
    options = [(f"@{login}", "Connected through GitHub CLI.") for login in available]
    options.append(("Enter a different username", "Useful before connecting the second account."))
    selected = choose(label, options)
    return available[selected - 1] if selected <= len(available) else ask(label)


def create_config(path: Path, *, target: str = "", helper: str = "") -> Config:
    ui = Ui()
    ui.banner()
    ui.step(1, "Choose the two accounts", "Both accounts must belong to you or authorize the test.")
    accounts = connected_accounts()
    if accounts:
        ui.success("GitHub CLI: " + ", ".join(f"@{login}" for login in accounts))
    else:
        ui.note("No connected GitHub CLI account found. Run the Connect command next.")
    target = target or choose_account("Target GitHub account", accounts)
    helper = helper or choose_account("Helper GitHub account", accounts, exclude=target)
    ui.step(2, "Keep evidence isolated", "Private is the recommended default.")
    repo = ask("Evidence repository name", default="achievement-lab-private")
    visibility_index = choose(
        "Repository visibility",
        [("Private (recommended)", "The repetitive event trail stays access-controlled."),
         ("Public", "Use only when the evidence itself helps readers.")],
    )
    config = Config(
        target_login=target,
        helper_login=helper,
        evidence_repo=repo,
        visibility="private" if visibility_index == 1 else "public",
    )
    config.validate()
    path.write_text(json.dumps({
        "target_login": config.target_login,
        "helper_login": config.helper_login,
        "evidence_repo": config.evidence_repo,
        "visibility": config.visibility,
        "default_branch": config.default_branch,
        "delay_seconds": config.delay_seconds,
        "safe_batch_limit": config.safe_batch_limit,
    }, indent=2) + "\n")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    ui.success(f"Saved local config to {path}")
    ui.note("This file is ignored by Git. Run the guided mode again to continue.")
    return config


def guided_mode(config_path: Path) -> int:
    ui = Ui()
    ui.banner()
    if not config_path.exists():
        if not connected_accounts():
            print("No GitHub account is connected yet. Let's use GitHub's official login first.\n")
            connect_github()
        print("\nNo local configuration was found. Let's create one.\n")
        create_config(config_path)
        return 0

    config = load_config(config_path)
    while True:
        accounts = connected_accounts()
        account_label = ", ".join(f"@{login}" for login in accounts) or "not connected"
        print(f"GitHub: {account_label}")
        print(f"Target: @{config.target_login}  ·  Evidence: {config.full_repo} ({config.visibility})\n")
        selected = choose("What would you like to do?", [
            ("Read the achievement atlas", "No account access and no writes."),
            ("Manage GitHub connection", "See connected accounts or use GitHub's official login."),
            ("Check my setup", "Verify credentials and the repository boundary."),
            ("Prepare the isolated lab", "Preview, then create or repair the evidence repository."),
            ("Run one controlled event", "Choose one scenario; the default count is always one."),
            ("Show evidence status", "Read counts from the isolated repository."),
            ("Exit", "Make no changes."),
        ])
        print()
        if selected == 1:
            catalog()
        elif selected == 2:
            connect_github()
        elif selected == 3:
            Lab(config).doctor()
        elif selected == 4:
            Lab(config, dry_run=True).init()
            print()
            confirm(f"Create only {config.full_repo}?", yes=False, dry_run=False)
            Lab(config).init()
        elif selected == 5:
            scenario_index = choose("Choose one event", [
                ("Quickdraw", "Create and immediately close one labelled issue."),
                ("YOLO event test", "Merge one author-created PR without review; award is uncertain."),
                ("Pull Shark", "Create one PR and let the helper merge it."),
                ("Pair Extraordinaire", "Create one genuinely co-authored commit."),
                ("Back", "Return without writing."),
            ])
            if scenario_index == 5:
                continue
            scenario = SUPPORTED[scenario_index - 1]
            Lab(config, dry_run=True).add(scenario, 1)
            print()
            confirm(f"Run exactly 1 x {scenario} in {config.full_repo}?", yes=False, dry_run=False)
            Lab(config).add(scenario, 1)
        elif selected == 6:
            Lab(config).status()
        else:
            ui.success("Nothing else was changed.")
            return 0
        print("\n" + "─" * 64 + "\n")


def catalog(*, as_json: bool = False) -> None:
    """Print the read-only achievement catalog without loading credentials."""
    if as_json:
        print(json.dumps({"visible_tier_max": 4, "achievements": ACHIEVEMENTS}, indent=2))
        return
    print("Achievement Lab catalog (observed checkpoints, not GitHub contracts)")
    print("Visible tier ceiling: x4; there is no visible x8 tier.\n")
    for achievement in ACHIEVEMENTS:
        tiers = " / ".join(
            f"x{index}: {count}" for index, count in enumerate(achievement["tiers"], start=1)
        )
        if not tiers:
            tiers = "not tiered"
        print(f"{achievement['name']} [{achievement['automation']}] — {tiers}")
        print(f"  {achievement['route']}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--config", default="achievement-lab.json")
    root.add_argument("--dry-run", action="store_true")
    root.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    commands = root.add_subparsers(dest="command")
    commands.add_parser("wizard", help="open the guided, interactive experience")
    commands.add_parser("connect", help="connect GitHub through the official gh login flow")
    setup = commands.add_parser("setup", help="create a safe local configuration")
    setup.add_argument("--target", default="")
    setup.add_argument("--helper", default="")
    catalog_parser = commands.add_parser("catalog", help="print the read-only achievement atlas")
    catalog_parser.add_argument("--json", action="store_true", dest="as_json")
    commands.add_parser("doctor")
    init = commands.add_parser("init")
    init.add_argument("--yes", action="store_true")
    commands.add_parser("status")
    add = commands.add_parser("add")
    add.add_argument("scenario", choices=SUPPORTED)
    add.add_argument("--count", type=int, default=1)
    add.add_argument("--yes", action="store_true")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        config_path = Path(args.config)
        if args.command is None:
            if sys.stdin.isatty():
                return guided_mode(config_path)
            parser().print_help()
            return 0
        if args.command == "wizard":
            return guided_mode(config_path)
        if args.command == "connect":
            connect_github()
            return 0
        if args.command == "setup":
            create_config(config_path, target=args.target, helper=args.helper)
            return 0
        if args.command == "catalog":
            catalog(as_json=args.as_json)
            return 0
        config = load_config(config_path)
        lab = Lab(config, dry_run=args.dry_run)
        if args.command == "doctor":
            lab.doctor()
        elif args.command == "status":
            lab.status()
        elif args.command == "init":
            confirm(f"Initialize isolated repository {config.full_repo}", yes=args.yes, dry_run=args.dry_run)
            lab.init()
        elif args.command == "add":
            confirm(
                f"Add {args.count} x {args.scenario} only to {config.full_repo}",
                yes=args.yes,
                dry_run=args.dry_run,
            )
            lab.add(args.scenario, args.count)
        return 0
    except LabError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
