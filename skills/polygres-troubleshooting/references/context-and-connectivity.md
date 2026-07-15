# Context and connectivity

Confirm the installed contract and local context before interpreting a remote
failure.

```console
polygres --help
polygres config path
polygres --json whoami
polygres --json projects list
```

Use command-specific help for every later command. Record CLI version, exit
code, and sanitized stderr. Do not print environment variables or config-file
contents because they may expose an API key or other credential.

Classify `whoami` failures as local configuration, expired or absent
authentication, network reachability, or control-plane response errors. Do not
convert an authentication failure into a project-not-found diagnosis.

Select an exact project ID from the public list or an explicit user-provided
value. If names collide, input is fuzzy, or configuration and user input
disagree, report an ambiguous project and stop. Never fuzzy-match a project.
