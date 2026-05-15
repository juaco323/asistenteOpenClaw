FROM python:3.12-alpine
WORKDIR /srv
COPY panel_server.py /srv/panel_server.py
ENV LLM_TEST_LOG_PATH=/workspace/.llm-test-runs.jsonl
ENV LLM_TEST_PANEL_PORT=8080
EXPOSE 8080
CMD ["python", "/srv/panel_server.py"]
