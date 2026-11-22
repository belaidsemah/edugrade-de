FROM python:3.12-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
RUN useradd -r -u 10001 appuser
WORKDIR /app
COPY --from=build /install /usr/local
COPY --chown=10001:10001 app.py .
USER 10001
EXPOSE 5000
CMD ["gunicorn","--worker-tmp-dir","/dev/shm","-b","0.0.0.0:5000","app:app"]
