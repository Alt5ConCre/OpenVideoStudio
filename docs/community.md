# Community

How to participate in OpenVideoStudio beyond opening a PR — Discussions,
what each category is for, and the short version of how contribution
works. For the full contributor guide (branching, DCO, review process),
see [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## Discussions

[GitHub Discussions](../../discussions) is for conversation — usage
questions, ideas, and sharing what you made. It is **not** for bug
reports or well-formed feature requests; those go through
[Issues](../../issues) so they're trackable against a specific fix. See
`.github/ISSUE_TEMPLATE/config.yml` — blank issues are disabled and
usage questions are redirected here specifically to keep Issues focused
on actionable, trackable work.

### Announcements
Project updates, releases, and maintainer posts — e.g. the pinned
"Welcome to OpenVideoStudio" post and release notes discussions. Read
here to stay current; posting is maintainer-led.

### Ideas
Proposals for future features, before there's a PR (or sometimes before
there's even an issue). If your idea touches a shared interface
(`providers/base.py`, the review-gate mechanics, anything `core/` shares
with Media Remix), this is where it should start — see
`CONTRIBUTING.md`'s "What needs discussion first."

### Q&A
Installation and usage questions — "how do I configure X," "why did Y
fail on my machine." Check `docs/INSTALL.md`'s troubleshooting section
and [`HARDWARE.md`](HARDWARE.md) first; if it's still unclear, ask here,
not in Issues.

### Show and tell
Generated videos, workflows, and experiments. This is the closest thing
to a community gallery today — there's no separate workflow marketplace
(that's a long-term idea, not built — see `ROADMAP.md`'s Long-term
vision section). If you want your workflow more formally documented,
use the [Workflow share](../.github/ISSUE_TEMPLATE/workflow_share.md)
issue template instead, or a PR under `examples/`.

### General
Anything that doesn't fit the categories above.

### Q&A vs. Polls
Polls exists (GitHub's default category) for quick community votes when
a maintainer needs one — not a primary category for day-to-day use.

## How to contribute

The short version — full detail (branch naming, DCO sign-off, PR
template, review process) is in [`../CONTRIBUTING.md`](../CONTRIBUTING.md):

1. **Fork** the repository.
2. **Create a branch** from `main`.
3. **Make your changes** — with tests, if it touches pipeline behavior.
4. **Submit a Pull Request** using `.github/PULL_REQUEST_TEMPLATE.md`.

New here? Start with a Discussion or a
[good first issue](good-first-issues.md) before taking on something
large — see `CONTRIBUTING.md`'s "Good first issues" section.
