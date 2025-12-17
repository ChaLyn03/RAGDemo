You are preparing a short part description for fabrication and assembly stakeholders.

User request:
{request}

IR facts (best-effort extraction):
{facts}
v
Approved defaults from exemplars (authoritative):
{approved_defaults}

Other corpus excerpts (authoritative):
{context}

Hard constraints (must follow):
- Use ONLY facts stated in the User request, IR facts, Approved defaults, or Other corpus excerpts.
- If a fact is not stated anywhere above, write: "Not specified in provided input."
- You MUST incorporate exemplar-backed details when they exist in Approved defaults (materials, tolerances, fastener practices).
- Do NOT add any justifications or material properties unless explicitly stated above.
  Examples of disallowed additions unless stated: "known for strength", "corrosion resistant", "ensures reliability", etc.
- Output MUST be exactly 3 sections with these headings (verbatim):
  1) ## Overview
  2) ## Materials & tolerances
  3) ## Vibration reliability practices
- Keep each section short. No extra headers or titles.

Write the final Markdown now.
