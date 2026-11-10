FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

COPY serveur/ serveur/
COPY persistance/ persistance/

RUN mkdir -p /app/persistance/data

EXPOSE 8765

CMD ["python", "-m", "serveur.main", \
     "--adresse", "0.0.0.0", \
     "--port", "8765", \
     "--base", "persistance/data/budget.db"]