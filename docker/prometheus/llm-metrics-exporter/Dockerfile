FROM python:3.12-slim

WORKDIR /app
COPY docker/prometheus/llm-metrics-exporter/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY docker/prometheus/llm-metrics-exporter/exporter.py /app/exporter.py

ENV LLM_METRICS_PORT=9092
EXPOSE 9092
CMD ["python", "/app/exporter.py"]
