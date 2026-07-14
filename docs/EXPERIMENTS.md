# Experiment guide

## Observe before automating

Achievement criteria are not a stable public API. Run one scenario, preserve
the evidence, and allow GitHub time to propagate the result before adding more.

## Quickdraw

The lab creates and immediately closes a clearly labelled issue. Start with one.

## YOLO

The target account authors and merges a pull request without a review. The pull
request changes only a timestamped evidence file on a dedicated branch.

## Pull Shark

The target authors a pull request and the helper merges it. The helper must be a
collaborator on the evidence repository. Existing global progress is not
reliably exposed by GitHub, so avoid large `--to` batches.

## Pair Extraordinaire

The target creates commits with a `Co-authored-by` trailer referring to the
helper's verified GitHub noreply address. The lab defaults to one commit; do not
assume community-observed tier thresholds are current.

## Galaxy Brain

The commonly observed flow uses an answerable Q&A Discussion: one account asks,
the target answers, and the question author marks the response as accepted.
This lab leaves the scenario manual because Discussions availability, category
IDs, and permissions differ across account and organization plans.

## Starstruck and social achievements

Stars, sponsors, followers, reactions, and similar social signals must be real.
Achievement Lab does not automate them.
