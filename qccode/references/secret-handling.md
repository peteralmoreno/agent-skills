# Q-C-Code Secret Handling Policy

The skill must be careful with secrets and ignored files.

## Never Copy Automatically

Never automatically copy:

- `.env`
- `.env.local`
- `.env.*`
- secrets
- tokens
- credentials
- private config
- SSH keys
- API keys
- cloud credentials
- ignored files that may contain secrets

## Ask First

If a local ignored config file appears required, ask the user before copying it.

Use wording like:

```text
This worktree may need `.env.local`, which can contain secrets. Do you want me to copy it, skip it, or create a sanitized `.env.example` instead?
```

## Prefer Documentation

Prefer creating or updating:

```text
.env.example
README.md
docs/setup.md
```

rather than copying secrets.

## Worktree Artifact

Record secret handling in `worktree.md`:

```md
## Gitignored Files

No secret-bearing files copied.

Required environment variables were documented in `.env.example`.
```

## Must Not

- Do not print secret values.
- Do not include secrets in artifacts.
- Do not commit secrets.
- Do not copy secret files without explicit approval.
