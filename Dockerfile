FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# Copy all project files needed for installation
COPY pyproject.toml README.md ./
COPY src/ ./src/
# Persist dep cache between builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && uv pip install -e .
# Verify import of package
RUN . .venv/bin/activate && \
    python -c "import mcp_py_repl" || { echo "Package import failed"; exit 1; }

FROM python:3.12-slim-bookworm
WORKDIR /app
# Create non-root user
RUN useradd -m app && chown -R app:app /app
USER app
COPY --from=uv --chown=app:app /app/.venv /app/.venv
COPY --from=uv /usr/local/bin/uv /usr/local/bin/uv
COPY --chown=app:app src/ ./src/
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
EXPOSE 8000
ENTRYPOINT ["mcp-py-repl"]
