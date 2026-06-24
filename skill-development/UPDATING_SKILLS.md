# Updating Skills for Upstream Package Changes

This guide is for the recurring task: **"check whether the skills need updates"**
because the underlying tidymodels packages have changed. It covers three phases —
**detect**, **plan**, and **execute**.

Skills in this repo describe and reference the *current* state of tidymodels
packages (yardstick, recipes, parsnip, dials, and the user-facing tidymodels
workflow). When those packages release new versions, the skills can drift out of
date in ways that `build-verify.py` cannot catch — because `build-verify.py` only
validates internal markdown links and file references, not whether the skills
match upstream reality.

> **Important:** This workflow ends at "changes made and verified." It does **not**
> commit. The user always handles git commit/tag/release themselves — see
> [RELEASING.md](RELEASING.md).

---

## Phase 1: Detect

When asked to check for needed updates, look for these categories of drift. Each
is something that has actually bitten this project.

### 1. New CRAN / upstream releases

For each package a skill covers, find out whether there's a newer version than the
skill currently assumes:

- Check the package's `NEWS.md` (in its GitHub repo or on CRAN) for what changed.
- Compare against the version referenced in the skill's content and examples.

Packages currently covered: **yardstick, recipes, parsnip, dials** (developer
skills) and the broader **tidymodels** stack (user skill).

### 2. Renamed, moved, or consolidated source files

Skills' `references/*.md` files cite specific source files (e.g. `R/grids.R`,
`R/extract.R`). When a package reorganizes its source, those citations go stale.

Real examples from past updates:

- dials consolidated `R/grid_regular.R`, `R/grid_random.R`, `R/grid_latin_hypercube.R`,
  `R/grid_max_entropy.R` into `R/grids.R` (regular + random) and `R/space_filling.R`.
- dials moved `R/extract_parameter_set_dials.R` → `R/extract.R`.
- yardstick and recipes renamed scripts referenced by the skills.

**How to check:** grep the skill's references for `R/` paths and confirm each file
still exists in the current package source.

### 3. Renamed / removed / added exported functions and arguments

- Exported functions referenced in examples or prose that were renamed or removed.
- New arguments, or changed argument names.
- Changed default values, or new valid values for an argument. (Example: dials'
  `values_weight_func` gained `"cos"` (renamed from `"cosine"`) and `"inv"`,
  going from 8 to 9 values — the skill's example and output comments had to match.)

### 4. Deprecations and lifecycle changes

Functions or arguments newly marked deprecated/superseded/experimental. Skills
should stop recommending deprecated APIs and point at the replacement.

### 5. New extension points worth documenting

New metrics, recipe steps, parsnip models/engines, or dials parameters that the
skill could now mention or use as examples.

### Where to look

- **`repos/`** — clone or `git pull` the relevant package repo here for reference
  (see project CLAUDE.md). This is the fastest way to diff source layout and read
  current `NEWS.md`.
- The package's `NEWS.md` is the highest-signal source for what changed.
- The installed package version (`packageVersion("dials")` in R) vs. CRAN.

---

## Phase 2: Plan

Before editing, scope the work:

1. **List affected skills and the specific files within them.** Map each upstream
   change to the `references/*.md`, `SKILL.md`, example code, or eval files it touches.
2. **Decide source vs. extension impact.** Developer skills document both
   *extension* development (`package::`, no internal `:::`) and *source*
   development (contributing to the package). A change may affect one or both.
3. **Watch for shared references.** If the affected file originated from
   `developers/shared-references/` or `developers/shared-references-parsnip/`, edit
   the **source** there — never the generated copy in a skill's `references/`
   folder. To check:

   ```bash
   find developers/shared-references developers/shared-references-parsnip -name "<filename>"
   ```

4. **Note doc-site impact.** Structural changes (new/renamed reference files) need
   matching `.qmd` files under `docs/`.

---

## Phase 3: Execute

1. **Make the edits** to the source markdown / examples.

   - Keep extension examples using the `package::` prefix and valid for the current
     package version.
   - Update output comments in examples if the package's output changed.

2. **Use the repository scripts for file operations** — never raw `mv`/`sed`/`awk`:

   - Renaming files: `skill-development/rename-and-update.py` (updates all references).
   - Surgical text replacement: `skill-development/replace-text.py`.

3. **Run the build/verify pipeline** from the project root until it reports SUCCESS:

   ```bash
   ./skill-development/build-verify.py
   ```

   This rebuilds shared files into each skill's `references/`, formats markdown,
   verifies all links and file references, and confirms docs `.qmd` coverage.

4. **(Optional) Render the docs site** to catch rendering issues:

   ```bash
   cd docs && quarto render
   ```

5. **Update evals/grading if behavior changed**, so tests reflect the new guidance.

6. **Stop and report.** Summarize what changed and which skills were affected. Do
   not commit — hand off to the user. When this rolls into a release, follow
   [RELEASING.md](RELEASING.md).
