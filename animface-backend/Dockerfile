FROM python:3.11-slim

# System dependencies for OpenCV + ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories
RUN mkdir -p uploads/originals uploads/animated logs \
    && chmod +x start-render.sh

EXPOSE 8000

CMD ["bash", "./start-render.sh"]
