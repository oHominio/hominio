# Use NVIDIA CUDA base image for GPU support
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

# Set environment variables for CUDA
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    portaudio19-dev \
    ffmpeg \
    git \
    curl \
    build-essential \
    alsa-utils \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch for CUDA 12.1 (compatible with KokoroEngine)
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for headless operation (RealtimeSTT server example pattern)
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
# Suppress ALSA errors in headless environment
ENV ALSA_PCM_CARD=-1
ENV ALSA_PCM_DEVICE=-1
ENV ALSA_MIXER_CARD=-1
ENV ALSA_MIXER_DEVICE=-1
# Redirect ALSA errors to null
ENV ALSA_CARD=none
# Additional audio suppression
ENV SDL_AUDIODRIVER=dummy
ENV PULSE_RUNTIME_PATH=/tmp/pulse-runtime

# Expose port
EXPOSE 8080

# Start the FastAPI application directly
CMD ["python3", "main.py"] 