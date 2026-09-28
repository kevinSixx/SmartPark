FROM paddlepaddle/paddle:2.6.2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLAGS_use_mkldnn=0 \
    OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel

RUN python -m pip install -r /app/requirements.txt

COPY . /app/ocr

EXPOSE 8002

CMD ["uvicorn", "ocr.main:app", "--host", "0.0.0.0", "--port", "8002"]