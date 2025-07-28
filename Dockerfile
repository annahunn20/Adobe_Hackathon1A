FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY main.py .
COPY utils.py .


RUN mkdir -p /app/input /app/output


RUN chmod +x main.py


CMD ["python", "main.py"]