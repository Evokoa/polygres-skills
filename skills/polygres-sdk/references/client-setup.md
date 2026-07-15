# Client setup

## Install and configure

`polygres-sdk` is the application package. `polygres-cli` is a separate
operational package. Add only the SDK to an application environment and follow
the repository's dependency-installation policy.

Keep credentials in server-side environment configuration:

```python
import os

from polygres import Polygres

client = Polygres(
    api_key=os.environ["POLYGRES_API_KEY"],
    runtime_url=os.environ["POLYGRES_RUNTIME_URL"],
)
project = client.project()
```

Import public symbols from `polygres`. Do not import or annotate with internal
namespace classes such as `Project`, `GraphNamespace`, or `VectorNamespace`;
they are not exported by the package. Prefer inferred local types or define an
application-owned `Protocol` when a function needs a mockable client contract.

Never log either environment variable, the authorization header, or the
client's private fields. Do not expose SDK calls from browser code.

## Select the correct endpoint

Use the per-project Runtime API URL from the project's Connect surface.

- Do not use the central control-plane URL.
- Do not use a direct or pooled Postgres URL.
- Do not derive or probe a private endpoint or private route.
- Require HTTPS outside an explicitly isolated local test.

The Runtime API already identifies the project, so `client.project()` is the
normal form. Pass a project ID only when the deployed API contract requires it
and the ID was resolved from trusted application context.

## Readiness and connection information

Check readiness before executing retrieval that depends on configured indexes:

```python
readiness = project.readiness()

if not readiness.graph.get("ready"):
    raise RuntimeError("graph retrieval is not ready")
if not readiness.vector.get("ready"):
    raise RuntimeError("vector retrieval is not ready")
```

Use connection information only when the application needs safe database
metadata:

```python
connection = project.connection_info()

print(connection.direct_host)
print(connection.pooled_host)
print(connection.pooled_url_without_password)
```

`project.connection_info()` returns passwordless direct and pooled URLs. It
does not return a database password. Do not append a password or put one in a
command argument, log, exception, or generated source file.

## Lifecycle

Close long-lived clients during application shutdown, or use a context manager:

```python
import os

from polygres import Polygres

with Polygres(
    api_key=os.environ["POLYGRES_API_KEY"],
    runtime_url=os.environ["POLYGRES_RUNTIME_URL"],
) as client:
    status = client.project().readiness()
```
