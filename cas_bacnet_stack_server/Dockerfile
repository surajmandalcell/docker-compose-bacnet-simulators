FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir bacpypes==0.18.7

COPY cas_bacnet_stack_server.py .

EXPOSE 47808/udp

CMD ["python", "-u", "cas_bacnet_stack_server.py"]