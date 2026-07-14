# Private evidence and public profiles

Achievement Lab separates the code people inspect from the events used in an
experiment. The runner can keep evidence in a private repository while the tool
itself remains public and reviewable.

## What remains private

- timestamped evidence files;
- generated branches;
- issue and pull-request timelines;
- controlled Q&A discussions;
- collaborator-only event links.

GitHub may still show an earned achievement on the profile. People without
repository access cannot open the private event links behind it.

## What remains public

- this runner and its safety boundary;
- the documented experiment method;
- the fact that the evidence is controlled;
- the profile achievement, if GitHub awards and displays it.

## Visibility checklist

1. Use a repository name containing `achievement-lab`.
2. Set `visibility` to `private` in the local config.
3. Confirm the repository returns `404` when requested without authentication.
4. Keep private contributions and achievements enabled in GitHub profile settings.
5. Never move generated evidence into an unrelated production repository.

Private does not mean secret methodology. It means the repetitive event trail
does not overwhelm the public project that explains the methodology.
