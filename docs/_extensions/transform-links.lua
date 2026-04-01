-- Lua filter to transform .md links to .qmd links in included content
-- This allows us to include original markdown files without modification

function Link(el)
  local target = el.target

  -- Transform .md to .qmd (including anchors)
  if target:match("%.md") then
    target = target:gsub("%.md", ".qmd")
  end

  -- Handle cross-skill SKILL references: ../add-xxx/SKILL.qmd -> add-xxx.qmd
  if target:match("%.%./[^/]+/SKILL%.qmd") then
    target = target:gsub("%.%./([^/]+)/SKILL%.qmd", "%1.qmd")
  end

  -- Handle cross-skill reference files from references/ folder:
  -- ../../add-xxx/references/file.qmd -> file.qmd
  -- (Keep in same references/ folder, just get the filename)
  if target:match("%.%./%.%./[^/]+/references/") then
    target = target:gsub("%.%./%.%./[^/]+/references/([^/]+)", "%1")
  end

  -- Handle same-skill reference files: add-xxx/references/file.qmd -> references/file.qmd
  if target:match("^add%-[^/]+/references/") then
    target = target:gsub("^add%-[^/]+/references/", "references/")
  end

  -- Remove developers/ prefix
  target = target:gsub("^developers/", "")

  el.target = target
  return el
end
