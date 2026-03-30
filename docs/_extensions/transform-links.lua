-- Lua filter to transform .md links to .qmd links in included content
-- This allows us to include original markdown files without modification

function Link(el)
  local target = el.target

  -- Only transform if it ends with .md
  if target:match("%.md$") then
    -- Transform any .md link to .qmd
    el.target = target:gsub("%.md$", ".qmd")
    return el
  end

  return el
end
