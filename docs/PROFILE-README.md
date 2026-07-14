# Profile README playbook

A strong profile README is a landing page, not a résumé dump. It should answer three questions in a few seconds: what do you build, which work should I open, and how can I reach you?

## Create the special repository

GitHub displays a profile README when all of these are true:

1. Create a repository named **exactly like your username**. For `octocat`, that is `octocat/octocat`.
2. Make it **public**.
3. Add a non-empty `README.md` in the repository root.

```bash
USER="octocat"
gh repo create "$USER/$USER" --public --add-readme \
  --description "Profile README for @$USER"
```

The command is an example, not something the Achievement Lab runner executes. If a profile repository already exists, clone and review it before editing.

Official guide: [Managing your profile README](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme).

## A useful page order

1. **One-line position** — what you build and for whom.
2. **Two or three proof projects** — outcome first, technology second.
3. **Working principles** — a small set of choices people can remember.
4. **Current focus** — one honest sentence, kept fresh.
5. **Contact** — a website or email route with a clear purpose.

Keep project details in project repositories. The profile should route people, not reproduce every README you have written.

## Start from the included template

Copy [`templates/profile/README.md`](../templates/profile/README.md) into your username repository and replace every `{PLACEHOLDER}`. The template uses plain GitHub Markdown, restrained badges, accessible alt text, and a static squircle surface.

```bash
cp templates/profile/README.md ../octocat/README.md
cp -R templates/profile/assets ../octocat/assets
```

Preview the diff before committing. Do not copy another person's name, artwork, statistics, or claims.

## Light and dark artwork

GitHub supports media conditions in HTML. Use them when one asset cannot remain legible in both themes:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
  <img alt="A concise description of the profile" src="assets/hero-light.svg" width="100%">
</picture>
```

Static SVGs are usually smaller and calmer than animated banners. Give every meaningful image useful alt text; use empty alt text for purely decorative images.

## Pins are the product shelf

GitHub lets you pin up to six public repositories and gists combined. Use all six only when each one adds a different proof:

- flagship product;
- technically demanding project;
- polished small utility;
- open-source collaboration;
- documentation or research work;
- current active project.

Put the strongest pair first. Make each repository's description, topics, social preview, README opening, and license coherent before pinning it.

Official guide: [Pinning items to your profile](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile).

## Private work without exposing repositories

GitHub can show anonymized private contribution counts and allow private activity to count toward visible Achievements. Visitors without access do not receive repository details. Configure this under profile contribution settings; do not claim confidentiality beyond what GitHub documents.

Official guide: [Manage visibility settings for private contributions and Achievements](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements).

## Final review

- Does the first screen explain the work without scrolling?
- Are the two strongest links obvious?
- Is every claim supported by a repository, release, demo, or documentation?
- Does the page work in light and dark themes and on a narrow screen?
- Are live counters and third-party cards necessary, reliable, and privacy-appropriate?
- Is the README fast enough that the work appears before decoration?

The best profile feels edited. Empty space is part of the design.
