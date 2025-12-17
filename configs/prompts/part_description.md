You are preparing a short part description for fabrication and assembly stakeholders.

User request (verbatim):
{request}

FACTS (from request / IR extraction):
{facts}

APPROVED DEFAULTS (from exemplars; treat as recommendations, not required facts):
{approved_defaults}

Reference materials (templates, style rules, glossary):
{context}

Hard constraints (must follow):
- Facts take priority. Only treat APPROVED DEFAULTS as recommendations unless the same fact appears in FACTS.
- If you use an item that comes only from APPROVED DEFAULTS, label it "Recommended default (from exemplar): ...".
- If a fact is not stated in FACTS or APPROVED DEFAULTS, write: "Not specified in provided input."
- You MUST cover exemplar-backed details when they exist in APPROVED DEFAULTS (materials, tolerances, fastener practices), using the labeling rule above.
- Output MUST be exactly 3 sections with these headings (verbatim):
  1) ## Overview
  2) ## Materials & tolerances
  3) ## Vibration reliability practices
- Keep each section short. No extra headers or titles.

Write the final Markdown now.
