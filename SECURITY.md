# Security policy

## Credential handling

- Prefer `gh auth login --web` over copying tokens into files or chat.
- Use dedicated test accounts and short-lived credentials.
- Never commit `.env`, tokens, cookies, or `~/.config/gh/hosts.yml`.
- Review authenticated accounts with `gh auth status` before every run.
- Revoke credentials when the experiment is finished.

## Repository boundary

The runner rejects repository names that do not contain `achievement-lab` and
does not implement deletion, visibility changes, profile README updates, stars,
follows, or writes to arbitrary repositories.

## Reporting a vulnerability

Open a private security advisory in this repository. Do not publish credentials
or an exploit containing another person's data.
