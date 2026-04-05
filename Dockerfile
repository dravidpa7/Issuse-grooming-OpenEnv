FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Required env vars (per hackathon guidelines)
# API_BASE_URL and MODEL_NAME have defaults; HF_TOKEN must be supplied at runtime.
ENV API_BASE_URL="https://api.openai.com/v1"
ENV MODEL_NAME="gpt-4.1-mini"
ENV HF_TOKEN=""

# inference.py is in the root directory — hackathon requirement
CMD ["python", "inference.py"]
