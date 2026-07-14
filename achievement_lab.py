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

VERSION = "1.1.0"
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
    commands = root.add_subparsers(dest="command", required=True)
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
        if args.command == "catalog":
            catalog(as_json=args.as_json)
            return 0
        config = load_config(Path(args.config))
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
