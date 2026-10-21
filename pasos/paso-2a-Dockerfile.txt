# PASO 2a: copiá este archivo a la raíz del repo como "Dockerfile" (sin .txt).
FROM python:3.12-slim
WORKDIR /app
COPY hola.py .
CMD ["python", "hola.py"]
