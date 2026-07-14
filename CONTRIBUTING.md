# Contributing

Small, reviewable changes are welcome.

1. Keep all generated activity isolated and explicitly labelled.
2. Add a dry-run path before adding any mutation.
3. Never add automated stars, follows, sponsors, or unrelated third-party activity.
4. Document observed behavior as observation, not as a guaranteed GitHub rule.
5. Run `python3 -m unittest discover -s tests -v` before opening a pull request.

## Proposing an observation

Use the observation issue form. Include the achievement name, the smallest event
you performed, whether the evidence was public or private, and an approximate
propagation window. Redact credentials and private repository details.

An observation may improve a confidence note; it does not automatically turn a
community threshold into an official rule.

## Pull requests

- Explain the reader problem before the implementation.
- Keep the visual system static, accessible, and lightweight.
- Add tests for runner behavior.
- Do not add new write capabilities without a dry run, explicit confirmation,
  a hard repository boundary, and a documented reason.
