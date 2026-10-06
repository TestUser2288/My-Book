-- Filtre pandoc : transforme les « callouts » Markdown (blockquotes commençant par un emoji)
-- en boîtes tcolorbox colorées, et remplace les emojis absents des polices LaTeX.

local kinds = {
  ["💡"] = "intuition", ["📐"] = "rigueur", ["🛠"] = "application", ["⚠"] = "attention",
  ["🧪"] = "remarque", ["📒"] = "cahier", ["✅"] = "retenir", ["🧭"] = "repere", ["📦"] = "donnees",
}

-- Remplacement de caractères dans le texte courant (polices Pagella sans ces glyphes)
local subst = {
  ["⭐"] = "{\\symfont\\color{etoile}★}", ["➕"] = "{\\symfont ⊕}",
  ["✅"] = "{\\symfont\\color{vert}✓}", ["❌"] = "{\\symfont\\color{rouge}✗}",
  ["✔"] = "{\\symfont\\color{vert}✔}", ["✓"] = "{\\symfont\\color{vert}✓}",
  ["✗"] = "{\\symfont\\color{rouge}✗}", ["✘"] = "{\\symfont\\color{rouge}✘}",
  ["⟹"] = "{\\symfont ⟹}", ["►"] = "{\\symfont ►}", ["▼"] = "{\\symfont ▼}",
  ["↔"] = "{\\symfont ↔}", ["⚠"] = "{\\symfont ⚠}", ["∝"] = "{\\symfont ∝}",
  ["💡"] = "{\\symfont\\color{bleu}■}", ["📐"] = "{\\symfont\\color{violet}■}",
  ["🛠"] = "{\\symfont\\color{aqua}■}", ["🧪"] = "{\\symfont\\color{gray}■}",
  ["🧭"] = "{\\symfont\\color{gray}■}", ["📦"] = "{\\symfont\\color{gray}■}",
  ["📒"] = "{\\symfont\\color{etoile}■}", ["🏋"] = "", ["\u{FE0F}"] = "", ["₀"] = "\\textsubscript{0}", ["₁"] = "\\textsubscript{1}", ["₂"] = "\\textsubscript{2}", ["⁴"] = "\\textsuperscript{4}", ["ʳ"] = "\\textsuperscript{r}", ["ᵉ"] = "\\textsuperscript{e}",
}

local function fix_str(s)
  if s.text:find("[^%z\1-\127]") then
    local out = s.text
    local changed = false
    for k, v in pairs(subst) do
      if out:find(k, 1, true) then
        out = out:gsub(k:gsub("%p", "%%%0"), (v:gsub("%%", "%%%%")))
        changed = true
      end
    end
    if changed then return pandoc.RawInline("latex", out) end
  end
end


local function first_inline(block)
  if (block.t == "Para" or block.t == "Plain") and #block.content > 0 then
    return block.content[1]
  end
end

local function BlockQuote(bq)
  local first = bq.content[1]
  if not first then return nil end
  local fi = first_inline(first)
  if not fi or fi.t ~= "Str" then return nil end
  local kind
  for emo, name in pairs(kinds) do
    if fi.text:find(emo, 1, true) == 1 then kind = name; break end
  end
  if not kind then return nil end
  -- retirer l'emoji (et l'espace qui suit) du premier paragraphe
  local content = first.content
  table.remove(content, 1)
  if content[1] and (content[1].t == "Space" or content[1].t == "SoftBreak") then table.remove(content, 1) end
  local blocks = { pandoc.RawBlock("latex", "\\begin{callout}{" .. kind .. "}") }
  for _, b in ipairs(bq.content) do blocks[#blocks + 1] = b end
  blocks[#blocks + 1] = pandoc.RawBlock("latex", "\\end{callout}")
  return blocks
end

-- Pas de filet horizontal juste avant un chapitre (séparateur de l'assemblage)
local function Blocks(blocks)
  local out = {}
  for i, b in ipairs(blocks) do
    local nxt = blocks[i + 1]
    if b.t == "HorizontalRule" and (not nxt or (nxt.t == "Header" and nxt.level == 1)) then
      -- supprimé
    else
      out[#out + 1] = b
    end
  end
  return out
end


-- Dans le code (police mono) : les symboles absents de DejaVu Sans Mono deviennent du texte
local code_subst = { ["✓"] = "[OK]", ["✗"] = "[X]", ["✔"] = "[OK]", ["✘"] = "[X]", ["✅"] = "[OK]", ["❌"] = "[X]",
  ["📒"] = "(cahier)", ["💡"] = "(i)", ["📐"] = "(rigueur)", ["🛠"] = "(appli)", ["🧪"] = "(remarque)", ["🧭"] = "(repère)",
  ["⚠"] = "(!)", ["➕"] = "(+)", ["₀"] = "_0", ["₁"] = "_1", ["₂"] = "_2", ["⁴"] = "^4", ["\u{FE0F}"] = "" }
local function fix_code(text)
  local out, changed = text, false
  for k, v in pairs(code_subst) do
    if out:find(k, 1, true) then out = out:gsub(k:gsub("%p", "%%%0"), (v:gsub("%%", "%%%%"))); changed = true end
  end
  return out, changed
end
local function CodeBlock(cb)
  local t, ch = fix_code(cb.text)
  if ch then cb.text = t; return cb end
end
local function Code(c)
  local t, ch = fix_code(c.text)
  if ch then c.text = t; return c end
end

-- Écriture arabe (volume IV, section 2.4.4) : [texte]{.arabe} -> police DejaVu Sans, droite à gauche
local function Span(sp)
  if sp.classes:includes("arabe") then
    local inner = pandoc.write(pandoc.Pandoc({ pandoc.Plain(sp.content) }), "plain"):gsub("%s+$", "")
    return pandoc.RawInline("latex", "\\ar{" .. inner .. "}")
  end
end

-- ordre : d'abord les callouts (avant que les emojis ne soient remplacés), puis les caractères
return { { Span = Span, BlockQuote = BlockQuote, Blocks = Blocks, CodeBlock = CodeBlock, Code = Code }, { Str = fix_str } }
