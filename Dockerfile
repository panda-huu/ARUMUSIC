FROM python:3.10-slim

# System basics aur FFmpeg (Isme sudo nahi lagate)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pehle requirements install karte hain taaki build fast ho
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Ab baki ka code copy karo
COPY . .

CMD ["python3", "main.py"]
