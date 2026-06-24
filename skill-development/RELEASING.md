# Releasing the Skills Plugin

This project ships as a **Claude Code plugin / marketplace**, not an R package —
there is no `DESCRIPTION`. A release is: bump the version, record what changed, and
verify, then the **user** performs the git commit/tag/GitHub release.

> **The user always handles git.** Do not run `git commit`, `git tag`, or create
> GitHub releases — even when asked to "prepare a release," and even after
> `build-verify.py` passes. Make the edits, verify, then hand off.

> This document captures the current flow and is expected to grow as we make more
> releases.

---

## Where the version lives

The version is tracked in **two files that must stay in sync**:

- [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json) → `"version"`
- [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) → `metadata.version`

The version badge in the root `README.md` reads dynamically from
`marketplace.json`, and links to GitHub Releases (the canonical release surface).
Individual `SKILL.md` files do **not** carry version numbers.

## Semantic versioning (0.x series)

- **Patch** (`0.4.0 → 0.4.1`): internal-only changes — eval/grading tooling,
  build scripts, fixes with no effect on skill content users see.
- **Minor** (`0.4.0 → 0.5.0`): user-facing skill-content changes — updated guidance,
  reference fixes for new package versions, new examples, a new skill.
- **Major** (`→ 1.0.0`): reserved for declaring the plugin stable / a settled API
  and skill set.

When in doubt between patch and minor, ask the user.

---

## Release steps

1. **Decide the version bump** (see above). Confirm the level with the user if the
   changes are mixed.

2. **Bump both version files** to the new version — `plugin.json` and
   `marketplace.json` must match.

3. **Update [`CHANGELOG.md`](../CHANGELOG.md)** (Keep a Changelog format). Add a new
   version section dated today, grouped into Added / Changed / Fixed. Scope the
   entry to the commits being released — the changes on the release branch not yet
   on `main` are a good basis:

   ```bash
   git log --oneline main..HEAD
   ```

4. **Verify** from the project root until it reports SUCCESS:

   ```bash
   ./skill-development/build-verify.py developers/
   ```

   Note: `users/` currently fails this script because it has no `shared-references/`
   directory; that is a known pre-existing issue, not a release blocker.

5. **Stop and hand off to the user.** Report the bumped version, the changelog
   entry, and the remaining git steps for them to run themselves:

   - commit the version + changelog changes
   - merge the release branch to `main`
   - tag `vX.Y.Z` and cut a GitHub Release (the `CHANGELOG.md` section is ready to
     paste as the release notes)
