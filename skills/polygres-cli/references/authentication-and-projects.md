# Authentication and projects

## Authentication

Use browser authentication only:

```bash
polygres login
polygres whoami
polygres logout
```

`login` opens an approval URL and polls until approved, denied, expired, or
timed out. A browser-open failure is not fatal because the CLI prints the URL.
Never ask for a username, password, access token, refresh token, poll token, or
device code.

If an authenticated request refreshes unsuccessfully, the CLI removes local
tokens and exits `3`. Run `polygres login` again.

`whoami` displays the active/default organization. Use it when project-name
resolution is surprising or the active organization is uncertain.

## Project workflow

```bash
polygres projects list
polygres projects use <project-id-or-exact-name>
polygres projects status [project]
polygres projects create <name> [--no-wait] [--timeout <seconds>]
```

Project names are exact and case-sensitive. Ambiguous names exit `6`. Persist
only the resolved external project ID.

Resolution precedence for commands that accept a positional project is:

1. Positional project.
2. Global `--project` flag.
3. Selected project in local config.

For other project-scoped commands, `--project` overrides the selected project.
If no project resolves, tell the user to run `polygres projects list` or
`polygres projects use <project>`.

## Project creation

Project creation waits for initial provisioning by default. `--no-wait`
returns after submission. State the chosen name and active organization before
creating a project.

When readiness polling times out or becomes unavailable after creation, retain
the returned project ID and request ID. Do not invent an ID and do not repeat
the create request. Use `polygres projects status <project>` to continue
checking the created project.
