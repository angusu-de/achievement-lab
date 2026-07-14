# Responsible testing

Achievement Lab is built for controlled observation, not engagement farming. Automation is acceptable only where it creates small, transparent events between accounts you control and stays inside a repository created for that purpose.

## Hard boundaries

The runner does not implement:

- stars, follows, reactions, forks, or watchers as social signals;
- sponsorships or financial actions;
- mass Discussions, issues, pull requests, or reviews;
- activity in unrelated or third-party repositories;
- profile README changes;
- repository deletion, history rewriting, or force pushes;
- attempts to conceal automation from GitHub.

These are product decisions, not missing features.

## Preflight

Before every write:

1. Confirm both accounts belong to you or have explicitly authorized the test.
2. Use a dedicated repository whose name contains `achievement-lab`.
3. Keep it private when the event trail is not useful to readers.
4. Run `doctor`, then repeat the command with `--dry-run`.
5. Start with `--count 1`.
6. Read the printed target before confirming.
7. Wait for GitHub to propagate the event before repeating anything.

```bash
python3 achievement_lab.py --config achievement-lab.json doctor
python3 achievement_lab.py --config achievement-lab.json --dry-run add pull-shark --count 1
python3 achievement_lab.py --config achievement-lab.json add pull-shark --count 1
```

## Rate and volume discipline

The default batch ceiling is deliberately small. A ceiling is not a recommended batch size. Use one event for a base test, record the result, and stop when additional activity would only make a number larger.

Never run multiple copies concurrently. Respect GitHub's rate limits, abuse detection, Terms of Service, and Acceptable Use Policies. If GitHub returns a secondary-rate-limit or abuse warning, stop; do not rotate credentials or retry aggressively.

## Privacy is access control, not invisibility

Private evidence can keep event links inaccessible to visitors who lack repository access. GitHub may still show anonymized contribution counts or an Achievement when the profile's visibility settings allow it. Account owners and GitHub retain access to the activity.

See [Private evidence](PRIVATE_EVIDENCE.md) for the exact separation.

## A better success metric

Use the lab to answer a bounded question:

> Does this legitimate event qualify, and how long does profile propagation take?

Do not use it to manufacture the impression of community adoption. For that, build a project people voluntarily use, discuss, contribute to, and star.
