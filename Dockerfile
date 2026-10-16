FROM node:24-bookworm-slim AS frontend
WORKDIR /build
COPY frontend-v2/package*.json ./
RUN npm ci
COPY frontend-v2/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt requirements-ai.txt ./
ARG WITH_AI=false
RUN pip install --no-cache-dir -r requirements.txt
RUN if [ "$WITH_AI" = "true" ]; then pip install --no-cache-dir -r requirements-ai.txt; fi
COPY backend backend
COPY backend_v2 backend_v2
COPY scripts scripts
COPY migrations migrations
COPY alembic.ini docker-entrypoint.py ./
COPY --from=frontend /build/dist frontend-v2/dist
RUN useradd --create-home appuser && mkdir /data && chown appuser /data
USER appuser
ENV DATABASE_URL=sqlite:////data/dealer-v2.sqlite3
ENV APP_ENV=local AUTH_MODE=local PORT=8090
EXPOSE 8090
CMD ["python", "docker-entrypoint.py"]
