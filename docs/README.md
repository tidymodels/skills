# Quarto Website Documentation

This directory contains the Quarto website source for Claude Code skills.

## Building the Site

```bash
cd docs
quarto render
```

Or preview with live reload:

```bash
cd docs
quarto preview
```

## Architecture

### No Content Duplication

This site uses Quarto's `{{< include >}}` feature to include source content directly from the repository, with zero duplication:

- **User skills**: `docs/users/*.qmd` includes from `../users/` (3 lines: logo + include)
- **Developer skills**: `docs/developers/*.qmd` includes from `../developers/` (Phase 3)
- **Reference files**: Minimal 1-line wrappers that include original markdown

**No YAML front matter** - headers come from the included markdown to avoid duplication.

### Link Transformation

A Lua filter (`_extensions/transform-links.lua`) automatically transforms `.md` links to `.qmd` during the build process. This allows us to include original markdown files without modification.

**How it works:**
1. Original files contain links like `[text](references/file.md)`
2. Lua filter transforms them to `[text](references/file.qmd)` during rendering
3. Quarto renders .qmd files to .html in the output

### File Structure

```
docs/
├── _quarto.yml                    # Site configuration + Lua filter
├── _extensions/
│   └── transform-links.lua        # Link transformation filter
├── assets/logos/                  # Package logos
├── styles.css                     # Custom styling
├── index.qmd                      # Homepage
├── getting-started.qmd            # Getting started guide
├── users/
│   ├── index.qmd                 # User landing page
│   ├── tidymodels.qmd            # Includes ../../users/tabular-data-ml/SKILL.md
│   └── references/
│       ├── data-spending.qmd     # Includes ../../../users/tabular-data-ml/references/data-spending.md
│       ├── resampling.qmd        # Includes ../../../users/tabular-data-ml/references/resampling.md
│       └── ...                   # Other reference wrappers
└── developers/
    ├── index.qmd                 # Developer landing page
    └── ...                       # Phase 3
```

## Adding New Skills

### For User Skills

1. Create skill in `users/skill-name/` directory with `SKILL.md` and `references/`
2. Ensure `SKILL.md` starts with a markdown header: `# Skill Title`
3. Create thin wrapper: `docs/users/skill-name.qmd`
   ```markdown
   ![](../assets/logos/package.png){.skill-header-logo}

   {{< include ../../users/skill-name/SKILL.md >}}
   ```
4. Create wrappers for reference files (1 line each):
   ```markdown
   {{< include ../../../users/skill-name/references/file-name.md >}}
   ```
5. Add to sidebar in `_quarto.yml` with explicit titles:
   ```yaml
   - text: "Skill Name"
     href: users/skill-name.qmd
   - section: "References"
     contents:
       - text: "Reference Title"
         href: users/references/reference-name.qmd
   ```
   **Note:** Use `text:` and `href:` since wrapper files have no YAML front matter.

### For Developer Skills

Same pattern but include from `../developers/` directory.

## Maintenance

- **Update content**: Edit original files in `users/` or `developers/` directories
- **Fix links**: Links are automatically transformed by Lua filter
- **Add logos**: Place PNG files in `assets/logos/`
- **Style changes**: Edit `styles.css`

## Key Benefits

✅ Single source of truth - content lives in skill directories
✅ No duplication - wrapper files are 5 lines each
✅ Automatic link transformation via Lua filter
✅ Easy to maintain - edit originals, site auto-updates
✅ Fast builds - minimal processing overhead
