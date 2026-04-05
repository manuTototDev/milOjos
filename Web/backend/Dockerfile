# Intentar con imagen base mas ligera y menos steps
FROM python:3.11-slim AS base
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn python-multipart numpy opencv-python-headless insightface onnxruntime Pillow huggingface_hub
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app
COPY --chown=user main.py startup.py ./
EXPOSE 7860
CMD ["python", "startup.py"]
