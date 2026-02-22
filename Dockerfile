FROM python:3.12-slim AS builder
RUN pip install uv
WORKDIR /app
COPY requirements.txt .
RUN uv venv && \
    uv pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY /agent /app/agent
EXPOSE 6767
CMD ["python", "-m", "agent.kafka_handler"]
