FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend backend
COPY frontend frontend
RUN useradd --create-home appuser && mkdir /data && chown appuser /data
USER appuser
ENV DEALER_DB=/data/dealer.sqlite3
EXPOSE 8090
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8090"]
