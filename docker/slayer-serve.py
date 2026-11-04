"""SLayer REST entrypoint for compiler-mode sidecars.

Why not `slayer serve`: the CLI imports `slayer.demo` at module load, which
imports DuckDB unconditionally — and current DuckDB wheels SIGILL on
pre-AVX2 CPUs (verified 2026-11-04 on Xeon E5-2680 v2, which is also what
the target single-node fleet runs). Compiler mode (dry_run / validate)
never executes, so DuckDB is dead weight for us.

This launcher imports only `slayer.api.server` + the storage backend, both
verified AVX2-clean, and serves the exact same FastAPI app (REST + /health;
the MCP SSE mount comes along inertly).
"""

import os

import uvicorn

from slayer.api.server import create_app
from slayer.storage.base import resolve_storage


def main() -> None:
    storage = resolve_storage(os.environ.get("SLAYER_STORAGE", "/data/slayer.db"))
    app = create_app(storage=storage)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5143")),
        log_level=os.environ.get("UVICORN_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
