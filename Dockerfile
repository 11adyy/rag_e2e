FROM python:3.13-slim

WORKDIR /app

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copiar proyecto
COPY . .

# Instalar dependencias
RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.chatbot.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]