FROM python:3.11-slim
WORKDIR /app

COPY packages/seedream-sdk ./packages/seedream-sdk
COPY packages/seedream-mcp ./packages/seedream-mcp

RUN pip install --no-cache-dir \
    ./packages/seedream-sdk \
    ./packages/seedream-mcp

ENV MCP_TRANSPORT=sse
EXPOSE 8000
CMD ["python", "-m", "seedream_mcp"]
