# Playbook — AI playbook management Skill

Portable Agent Skill for **learning about, initializing, creating, discovering, using, reviewing, and improving** reusable AI playbooks.

A **Skill** delivers the instructions for how an agent does *playbook management*. The playbooks created with this Skill remain standalone `PLAYBOOK.md` files in a project or central playbook library; they are not auto-installed as Skills.

## Install

Copy the entire `playbook/` directory from this repository into your runtime's skills folder:

```powershell
# Claude Code
Copy-Item -Recurse playbook "$env:USERPROFILE\.claude\skills\playbook"

# Codex / portable Agent Skills installation
Copy-Item -Recurse playbook "$env:USERPROFILE\.agents\skills\playbook"
```

Review destination files before replacing an existing installation.

## Invoke

- `/playbook help` — explain the approach and available commands.
- `/playbook setup` — initialize `playbooks/` in the current project.
- `/playbook bank setup ~/my-playbook-bank` — initialize a **user-chosen central Playbook Bank**.
- `/playbook bank list` — discover playbooks in the selected Bank.
- `/playbook history incident-triage` — examine execution history stored in the Bank.
- `/playbook memory incident-triage` — review and propose durable lessons, with user-approved promotion.
- `/playbook create "investigate API latency"` — define and draft one bounded procedure.
- `/playbook list` — discover matching playbooks.
- `/playbook run incident-triage` — execute with explicit tools, permissions and evidence.
- `/playbook review incident-triage` — critique a draft.
- `/playbook improve incident-triage` — propose a candidate revision from runs.

On Codex or other runtimes, try `$playbook` or ask the agent to **use the playbook Skill**.

## Optional local CLI

From the **agent-skills repo root** (or substitute the installed absolute Skill path):

```bash
python3 playbook/scripts/pb.py init --root /path/to/project
python3 playbook/scripts/pb.py new incident-triage --root /path/to/project --description "Investigate API incidents"
python3 playbook/scripts/pb.py list --root /path/to/project
python3 playbook/scripts/pb.py validate --root /path/to/project
python3 playbook/scripts/pb.py prepare incident-triage --root /path/to/project --inputs inputs.json
python3 playbook/scripts/pb.py finish /path/to/project/playbooks/.runs/<run-id>.json --proof proof.json --result blocked
```

`prepare` and `finish` manage **records**, not model execution, service access or independent truth verification. The agent performs the work using its granted tools. `finish --result passed` requires all declared `P#` checks be self-reported as passed with evidence, but this is **not independent verification**.

See [setup and authoring](references/authoring.md), [execution and improvement](references/execution.md), [the canonical template](assets/playbook-template.md), and a [worked read-only PR inspection example](examples/inspect-pull-request/PLAYBOOK.md).

## Optional Playbook Bank (persistent, shared source)

A Playbook Bank is a **folder chosen by the user**, not an Agent Skill install. A single Bank can be reused from multiple repositories. Playbook versions remain independent; the Bank adds private execution history and curated memory.

\`\`\`bash
python3 playbook/scripts/pb.py bank init ~/my-playbook-bank
python3 playbook/scripts/pb.py bank info ~/my-playbook-bank
python3 playbook/scripts/pb.py new incident-triage --bank ~/my-playbook-bank \
  --description "Investigate incidents safely"
python3 playbook/scripts/pb.py list --bank ~/my-playbook-bank
python3 playbook/scripts/pb.py validate --bank ~/my-playbook-bank
python3 playbook/scripts/pb.py prepare incident-triage --bank ~/my-playbook-bank \
  --inputs inputs.json --allow-draft
# Finish the record path returned by prepare, after actual execution and checks:
python3 playbook/scripts/pb.py finish ~/my-playbook-bank/.state/runs/incident-triage/<run-id>.json \
  --proof proof.json --result blocked
python3 playbook/scripts/pb.py history incident-triage --bank ~/my-playbook-bank
python3 playbook/scripts/pb.py memory add incident-triage --bank ~/my-playbook-bank \
  --note "Check downstream connection limits early."
python3 playbook/scripts/pb.py memory list incident-triage --bank ~/my-playbook-bank --all
python3 playbook/scripts/pb.py memory approve incident-triage --bank ~/my-playbook-bank \
  --id m-xxxxxxxxxxxx --reviewer "reviewer-name"
\`\`\`

Approved notes are made available to *future prepared runs* as advisory, untrusted context. Proposals are not automatically remembered as authority, and neither \`prepare\` nor \`finish\` invokes an AI runtime. See [the full Bank guide](references/bank.md) for selection, provenance, local privacy and limitations.

## Default workspace layout

```text
project/
  playbooks/
    README.md
    incident-triage/
      PLAYBOOK.md
      references/        # optional, domain-specific
      scripts/           # optional, approved tools
    .gitignore           # excludes .runs/
    .runs/               # local execution records; not committed by default
```

No GitHub/Jira operations, issue creation, branch creation, PR posting, attachments or code changes happen merely by creating a playbook. Such operations require an explicit request and suitable authorization.

## Test

```bash
python3 -m unittest discover -s playbook/tests -v
```

This tests the standard-library CLI and file contracts, including bank history and memory. It does not assess the quality of AI decisions or proof truthfulness.
