# Ch 6: Multi-Stage Non-Root Production Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
RUN groupadd -g 10001 appgrp && \
    useradd -u 10001 -g appgrp -s /sbin/nologin appusr
COPY --from=builder /install /usr/local
COPY --chown=appusr:appgrp . /app
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s \
  CMD ["python3", "-c", "print('healthy')"]
ENTRYPOINT ["python3", "app.py"]
