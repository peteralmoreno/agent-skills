# oh-my-pi optional `/ray` alias

The portable skill itself works in oh-my-pi using `/skill:ray` (if skill commands are enabled). For a shorter literal `/ray` command, copy `commands/ray.md` to either:

- Project: `<repo>/.omp/commands/ray.md`
- User-level default profile: `~/.omp/agent/commands/ray.md`

Also install the **same** `ray/` skill folder at `<repo>/.omp/skills/ray/` or `~/.omp/agent/skills/ray/`. The command refers to `skill://ray` and therefore does not hardcode a filesystem location.

After reloading oh-my-pi, try:

```text
/ray We need a new event feed. I favor a dedicated Kafka topic but will consider other designs.
```

The wrapper is for oh-my-pi only. Claude Code already exposes the installed skill directly as `/ray` and doesn't need the command file. If your oh-my-pi uses named profiles or custom discovery configuration, adjust the installation path accordingly.
