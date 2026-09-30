# ============================================================
# SMARTPARK AI 2.8.1 - CPU
# ============================================================

FROM python:3.11-slim


# ============================================================
# VARIABLES
# ============================================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV TF_USE_LEGACY_KERAS=1
ENV DEEPFACE_HOME=/root


# ============================================================
# DIRECTORIO
# ============================================================

WORKDIR /app


# ============================================================
# DEPENDENCIAS SISTEMA
# ============================================================

RUN apt-get update && \
    apt-get install -y \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        ffmpeg \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# REQUIREMENTS
# ============================================================

COPY ai/requirements.txt /app/requirements.txt


# ============================================================
# PYTHON
#
# IMPORTANTE:
# Instalamos PyTorch CPU ANTES de Ultralytics.
# Así evitamos arrastrar CUDA / cuDNN / NVIDIA.
# ============================================================

RUN python -m pip install \
        --no-cache-dir \
        --upgrade pip setuptools wheel \
    && python -m pip install \
        --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch torchvision \
    && python -m pip install \
        --no-cache-dir \
        -r /app/requirements.txt


# ============================================================
# YOLO11n
# ============================================================

COPY edge/models/yolo11n.pt /app/yolo11n.pt


# ============================================================
# PRECARGA ARCFACE + RETINAFACE
# ============================================================

RUN python -c "\
import numpy as np; \
from deepface import DeepFace; \
print('[BUILD] Precargando ArcFace + RetinaFace...'); \
img=np.zeros((224,224,3), dtype=np.uint8); \
DeepFace.represent( \
    img_path=img, \
    model_name='ArcFace', \
    detector_backend='retinaface', \
    enforce_detection=False, \
    align=True \
); \
print('[BUILD] ArcFace + RetinaFace incluidos.')"


# ============================================================
# CODIGO
# ============================================================

COPY ai /app/ai


# ============================================================
# PUERTO
# ============================================================

EXPOSE 8001


# ============================================================
# HEALTHCHECK
# ============================================================

HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=180s \
    --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/ready', timeout=5)" || exit 1


# ============================================================
# START
# ============================================================

CMD ["uvicorn", "ai.main:app", "--host", "0.0.0.0", "--port", "8001"]
