FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY requirements.txt .
COPY pyproject.toml .

RUN uv pip install --system -r requirements.txt
RUN uv lock

COPY . .

ENV API_BASE_URL="https://openrouter.ai/api/v1"
ENV MODEL_NAME="qwen/qwen3.6-plus:free"
ENV HF_TOKEN=""

EXPOSE 7860

# Run from /app so relative imports work
CMD ["python", "server/app.py"]