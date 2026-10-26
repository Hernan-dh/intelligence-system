# Repository instructions

## Continuous documentation

- Document lasting functional, technical, or operational changes in the same change set.
- Update `docs/ARCHITECTURE.md` for components, data flows, integrations, or trust-boundary changes.
- Update `docs/OPERATIONS.md` for setup, verification, deployment, or publishing changes.
- Never add credentials, production data, traces, or generated databases to version control.

## Verification and publishing

- Run `python scripts/verify.py` before proposing a commit.
- Do not commit or push without explicit user authorization.
- `scripts/publish.py` requires an interactive `PUBLISH` confirmation and never force-pushes.
