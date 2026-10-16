# Stdio MCP server for local Docker / MCP hosts.
# Build: docker build -t tinyrex-mcp .
# Run:   docker run --rm -i -e APIFY_TOKEN=... tinyrex-mcp
FROM python:3.12-slim-bookworm
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["tinyrex-mcp"]
