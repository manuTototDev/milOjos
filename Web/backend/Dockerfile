FROM python:3.11-slim

# Install system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps (heaviest step, cached)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt huggingface_hub && \
    rm /tmp/requirements.txt

# Create non-root user
RUN useradd -m -u 1000 user

# Copy application code (as root, then chown)
WORKDIR /home/user/app
COPY main.py startup.py ./
RUN chown -R user:user /home/user/app

# Switch to non-root user
USER user

EXPOSE 7860
CMD ["python", "startup.py"]
