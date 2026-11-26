FROM python:3.11-slim AS builder
WORKDIR /build
COPY app/requirements.txt .
RUN pip install --no-cache-dir --upgrade "pip>=25.0" "setuptools>=78.1.1" "wheel>=0.46.2" "jaraco.context>=6.1.0" && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade "setuptools>=78.1.1" "wheel>=0.46.2" "jaraco.context>=6.1.0" && \
    pip uninstall -y pip setuptools wheel && \
    groupadd -g 1001 appgroup && useradd -u 1001 -g appgroup -m appuser
COPY --from=builder /install /usr/local
COPY app/app.py .
RUN chown -R appuser:appgroup /app
USER 1001:1001
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
