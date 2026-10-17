# LENS HTML — HTML-first, format-flexible companion

This standalone Agent Skill retains the same **LENS methodology** as [`lens`](../lens/), but defaults to accessible, self-contained HTML when no output format is specified. The unsuffixed skill defaults to its normal Markdown/text presentation. **Neither version restricts input or output to one file format.**

- Invoke `/lens-html` in Claude Code, `$lens-html` in Codex, or ask your agent to use the `lens-html` skill.
- Supply HTML, Markdown, prose, Jira text, or an accessible source path.
- Ask for `output .md`, `output .html`, `output Jira text` or an `HTML fragment` explicitly to override the default.
- Copy the entire `lens-html/` folder into your agent's skill directory to install independently.
- See [human notes](references/html-guide.md) and [HTML starter](assets/plan-template.html) if present.

This is a **presentation preference**, not a new workflow, an automatic file converter, a Jira ADF adapter, or permission to implement. See [format interoperability](../docs/format-interoperability.md) for the cross-skill format policy when browsing the full repository.
