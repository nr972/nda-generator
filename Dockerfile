FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

RUN mkdir -p data/generated

EXPOSE 8000

CMD ["uvicorn", "nda_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
