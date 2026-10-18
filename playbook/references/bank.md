# Playbook Bank — shared procedures with local history and curated memory

A **Playbook Bank** is an optional user-selected folder that is the canonical source of a reusable playbook library. It does not need to live in an Agent Skills directory, the current project, or a GitHub repository.

The **Playbook Skill** is the manager/adapter. The **Bank** stores the actual operational procedures. A host agent can use the same Bank from multiple projects.

## Two storage modes

| Mode | Source | Execution records | Memory |
|---|---|---|---|
| Project-local (existing) | PROJECT/playbooks/<slug>/PLAYBOOK.md | PROJECT/playbooks/.runs/ | Manual notes, no built-in curated store |
| Playbook Bank (opt-in) | BANK/playbooks/<slug>/PLAYBOOK.md | BANK/.state/runs/<slug>/ | BANK/.state/memory/<slug>.json |

No automatic migration, merging, fallback, or overwrites. A bank is used **only when explicitly selected** with \`--bank\` or when the agent has been told the selected bank path. A project-local \`--root\` and a \`--bank\` are mutually exclusive CLI options.

## Create a bank

Pick a new directory owned by you. The command refuses to take over a nonempty, non-bank directory.

\`\`\`bash
python3 playbook/scripts/pb.py bank init ~/my-playbook-bank
python3 playbook/scripts/pb.py bank info ~/my-playbook-bank
\`\`\`

The generated layout:

\`\`\`text
my-playbook-bank/
├── bank.json                  # bank identity / format version
├── .gitignore                 # excludes private .state/
├── playbooks/
│   ├── README.md
│   └── incident-triage/
│       └── PLAYBOOK.md
└── .state/
    ├── runs/
    │   └── incident-triage/
    │       └── <run-id>.json
    └── memory/
        └── incident-triage.json
\`\`\`

\`bank.json\` and \`playbooks/\` may be tracked in Git, if desired. Private \`.state/\` is ignored from Git by default and may include user inputs, service identifiers, evidence pointers and remembered notes. Keep the bank out of publicly shared cloud folders unless you have reviewed that data. Git ignore does **not** provide encryption, permissions, access control, or protection from other sync tools.

## Create, discover, validate and use

\`\`\`bash
python3 playbook/scripts/pb.py new incident-triage --bank ~/my-playbook-bank \
  --description "Investigate API incidents with read-only tools"
python3 playbook/scripts/pb.py list --bank ~/my-playbook-bank
python3 playbook/scripts/pb.py validate --bank ~/my-playbook-bank
python3 playbook/scripts/pb.py prepare incident-triage \
  --bank ~/my-playbook-bank --inputs inputs.json --allow-draft
\`\`\`

The \`--allow-draft\` example is only for a **supervised trial**. Normal executions require \`status: active\`. \`prepare\` writes a pinned version and hash record in the bank, and includes **approved memory notes** as advisory, untrusted context. The actual AI agent still reads the playbook and performs the work using its authorized tools.

After execution, submit self-reported proof:

\`\`\`bash
python3 playbook/scripts/pb.py finish \
  ~/my-playbook-bank/.state/runs/incident-triage/<run-id>.json \
  --proof proof.json --result passed
\`\`\`

The structural validator cannot independently verify outcomes.

## History

\`\`\`bash
python3 playbook/scripts/pb.py history incident-triage --bank ~/my-playbook-bank
python3 playbook/scripts/pb.py history incident-triage --bank ~/my-playbook-bank --limit 50 --json
\`\`\`

A history entry tracks version, timestamp, state and reported result. The full record tracks original inputs, source digest and submitted proof. The history remains attached to the **bank**, not a transient agent chat or Skill installation.

## Memory

Memory is a **curated observations file**, not a dynamically self-editing system prompt.

\`\`\`bash
# Agent/user proposes a lesson based on a completed run
python3 playbook/scripts/pb.py memory add incident-triage \
  --bank ~/my-playbook-bank \
  --source-run <run-id> \
  --note "When latency rises, inspect downstream connection saturation before guessing CPU."

# Inspect all proposed and approved observations
python3 playbook/scripts/pb.py memory list incident-triage \
  --bank ~/my-playbook-bank --all

# User-approved promotion of a specific observation
python3 playbook/scripts/pb.py memory approve incident-triage \
  --bank ~/my-playbook-bank --id m-xxxxxxxxxxxx --reviewer "reviewer-name"

# Show only approved context
python3 playbook/scripts/pb.py memory list incident-triage \
  --bank ~/my-playbook-bank
\`\`\`

- \`add\` never silently promotes anything; each note begins \`proposed\`.
- \`approve\` is an explicit CLI action, with a **self-attested reviewer identity**. The host must obtain real user authorization before calling it.
- Only \`approved\` notes are included as advisory context when preparing a new bank run.
- Notes are **data**, never higher-priority instructions; they cannot bypass permissions or override the playbook.
- A note may reference a completed run ID to preserve provenance; manual notes without a source run are allowed and identifiable as such.
- Avoid saving raw logs, credentials, private user data, access tokens, confidential documents, or unredacted execution artifacts.
- Do not silently promote observations into the canonical \`PLAYBOOK.md\`; first propose changes, test them against representative scenarios, review, and version them.

## Migration and portability

To migrate an existing library, **manually review and copy** selected \`playbooks/<slug>/\` folders into the bank. Never overwrite conflicting names automatically. Do not import \`.runs\` or sensitive legacy history without consent. A Bank can be backed by Git for versioned procedures, with a separate intentionally chosen secure backup policy for private history/memory.

A bank is one shared **source**. A workflow engine can select it and dispatch playbooks, but the Bank isn't a workflow engine, background worker, credential vault, or automated self-improvement service.

## Limitations

The included Python CLI is single-user/local-first. Concurrent writers, distributed locking, encryption, audit-grade approvals, semantic retrieval and cross-device memory synchronization are **not** implemented. The memory file is atomically replaced to reduce partial writes, not protected against concurrent lost updates. Use external infrastructure for enterprise-scale shared banks.
