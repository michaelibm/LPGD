FROM python:3.12-slim

WORKDIR /app

# Dependencias de sistema minimas (compilacao de libs como cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Volume para persistir banco de dados e chave de criptografia
VOLUME ["/app/data"]

ENV LGPD_MANAGER_DB_DIR=/app/data
ENV LGPD_MANAGER_ADMIN_EMAIL=admin@local
ENV LGPD_MANAGER_ADMIN_SENHA=TrocarSenha123!

EXPOSE 8811

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8811"]
