# Badges, topics, and proof

Use labels as a navigation system. A badge should answer a question; a topic should make the repository discoverable; a release should prove that the project is maintained.

## Repository topics

Choose five to ten precise, lowercase topics. Combine four kinds:

| Kind | Examples |
|---|---|
| problem | `image-optimization`, `system-diagnostics` |
| platform | `windows`, `browser`, `github-api` |
| implementation | `python`, `typescript`, `php` |
| quality | `privacy-first`, `local-first`, `accessible` |

Avoid vague topics such as `awesome`, duplicated synonyms, and technologies that only appear in tooling.

With GitHub CLI:

```bash
gh repo edit OWNER/REPO \
  --add-topic github-achievements \
  --add-topic reproducible-research \
  --add-topic python
```

## README badges

Keep the first row short. Useful categories are runtime, CI, release, license, and one project-specific promise.

```md
[![CI](https://github.com/OWNER/REPO/actions/workflows/test.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/OWNER/REPO?style=flat-square)](https://github.com/OWNER/REPO/releases)
[![License](https://img.shields.io/github/license/OWNER/REPO?style=flat-square)](LICENSE)
```

Badges are remote images. Prefer a small number from providers you trust, add descriptive alt text, and never use custom images that imitate GitHub's official Achievement artwork.

## Technology labels

When a stack list is genuinely useful, use text first or restrained static badges:

```md
**Built with:** Python · SQLite · GitHub REST API
```

```md
![Python](https://img.shields.io/badge/Python-3.10%2B-17181a?style=flat-square&logo=python&logoColor=white)
```

A wall of logos usually says less than one architecture sentence.

## Releases are stronger than decorative badges

A professional public project should make its state obvious:

- semantic or date-based version;
- short release notes focused on user impact;
- install or download instructions;
- checksums or signatures when artifacts are distributed;
- a clear support and security policy.

If no release artifact exists, do not add a release badge merely for appearance.

## Social preview

GitHub recommends a solid PNG, JPG, or GIF under 1 MB, at least 640×320 and ideally 1280×640. This repository includes [`assets/social-preview.png`](../assets/social-preview.png), generated from the same quiet visual system as its hero.

Upload it in **Repository Settings → Social preview**. Committing the file does not set it automatically.

Official guide: [Customizing your repository's social media preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview).

## What actually makes a project pinnable

1. A title and outcome visible in the first viewport.
2. A working install, demo, or reproducible example.
3. Screenshots that show the actual product.
4. A small architecture explanation where it adds trust.
5. Tests and a visible maintenance story.
6. License, contribution, security, and support boundaries.

Badges summarize those facts. They cannot create them.
