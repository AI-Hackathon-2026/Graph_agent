FROM python:3.12-slim
RUN pip install uv
WORKDIR /app
COPY requirements.txt .
RUN uv venv && uv pip install --no-cache-dir -r requirements.txt
COPY /agent /app/agent
EXPOSE 6767
CMD ["uv", "run", "python", "-m", "agent.kafka_handler"]
