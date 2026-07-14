# Achievement Lab

> Reproducible GitHub profile-achievement experiments, with explicit consent,
> isolated evidence, and a hard boundary around your real repositories.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-7c5cff.svg)](LICENSE)
[![Safety: isolated](https://img.shields.io/badge/Safety-isolated-15d1c5.svg)](SECURITY.md)

Achievement Lab is a small command-line tool for people who want to understand
which GitHub profile achievements can be reproduced and how long propagation
takes. It creates transparent evidence in one dedicated repository. It never
touches your profile README, existing repositories, stars, followers, or
third-party projects.

## Why this exists

GitHub describes Achievements as a public-preview feature whose behavior can
change. Community lists often mix observation, folklore, retired badges, and
outdated thresholds. This project keeps the experiment honest:

- two accounts you control;
- one repository created solely for evidence;
- every artifact prefixed with `ALAB`;
- a preview before every write;
- no fake social signals;
- no writes to the profile repository.

## Quick start

```bash
git clone https://github.com/angusu-de/achievement-lab.git
cd achievement-lab
cp examples/achievement-lab.example.json achievement-lab.json

gh auth login --hostname github.com --web
gh auth login --hostname github.com --web

python3 achievement_lab.py --config achievement-lab.json doctor
python3 achievement_lab.py --config achievement-lab.json init
python3 achievement_lab.py --config achievement-lab.json add quickdraw --count 1
python3 achievement_lab.py --config achievement-lab.json status
```

The second login is only needed for scenarios involving another account. Keep
the evidence repository private if you want the event trail hidden. Whether
private activity contributes to achievements depends on your GitHub profile
visibility settings.

## Supported scenarios

| Scenario | What the lab creates | Second account |
|---|---|---:|
| Quickdraw | One issue, immediately closed | No |
| YOLO | One author-created PR, merged without review | No |
| Pull Shark | Author-created PR, merged by helper | Yes |
| Pair Extraordinaire | Commits with a valid co-author trailer | Yes |

Galaxy Brain is documented in [the experiment guide](docs/EXPERIMENTS.md), but
is intentionally not automated yet because Discussions permissions and
categories vary between repositories.

Before attempting community-observed tiers, read the
[tier strategy](docs/TIER_STRATEGY.md) and the
[private-evidence guide](docs/PRIVATE_EVIDENCE.md).

## Safety model

The configured repository name must contain `achievement-lab`. Writes are
refused anywhere else. `--dry-run` prints the plan and exits before requesting a
mutation. Destructive operations, profile updates, repository deletion, stars,
follows, and activity outside the evidence repository are not implemented.

Read [SECURITY.md](SECURITY.md) before using long-lived credentials.

## Disclaimer

GitHub decides if and when an achievement appears. The project reports evidence
it created; it does not promise badges or stable thresholds. This project is not
affiliated with GitHub.

## License

MIT — see [LICENSE](LICENSE).
