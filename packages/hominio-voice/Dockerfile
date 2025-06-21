# Use NVIDIA CUDA base image with cuDNN for GPU support
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set environment variables for CUDA
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Force CUDA usage - NO CPU FALLBACKS
ENV CUDA_VISIBLE_DEVICES=0
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV FORCE_CUDA=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3.10-dev \
    build-essential \
    portaudio19-dev \
    ffmpeg \
    git \
    curl \
    alsa-utils \
    libasound2-dev \
    libsndfile1 \
    ninja-build \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Make python3.10 the default python/pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install PyTorch for CUDA 12.1 (matching the reference implementation)
RUN pip install --no-cache-dir \
    torch==2.5.1+cu121 \
    torchaudio==2.5.1+cu121 \
    torchvision==0.20.1 \
    --index-url https://download.pytorch.org/whl/cu121

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for headless operation and stability
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Comprehensive ALSA and audio suppression for headless environment
ENV ALSA_PCM_CARD=-1
ENV ALSA_PCM_DEVICE=-1
ENV ALSA_MIXER_CARD=-1
ENV ALSA_MIXER_DEVICE=-1
ENV ALSA_CARD=none
ENV SDL_AUDIODRIVER=dummy
ENV PULSE_RUNTIME_PATH=/tmp/pulse-runtime
ENV XDG_RUNTIME_DIR=/tmp

# Multiprocessing and threading stability fixes
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false
ENV PYTORCH_NUM_THREADS=1

# Create dummy ALSA config to suppress errors
RUN mkdir -p /root/.asoundrc.d && \
    echo "pcm.!default { type plug slave { pcm null } }" > /root/.asoundrc && \
    echo "ctl.!default { type hw card 0 }" >> /root/.asoundrc

# Create runtime directories
RUN mkdir -p /tmp/pulse-runtime && chmod 755 /tmp/pulse-runtime

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the FastAPI application
CMD ["python", "main.py"] 