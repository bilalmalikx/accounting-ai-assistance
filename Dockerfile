# ============================================
# STAGE 1: Backend Setup
# ============================================
FROM python:3.11-slim AS backend

WORKDIR /backend

# Install only runtime dependencies (no compilers)
RUN apt-get update && apt-get install -y \
    libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --retries 5 --timeout 200 -r requirements.txt

COPY app/ ./app/
COPY data/ ./data/
COPY .env .

RUN mkdir -p /backend/data/vector_store /backend/data/uploads /backend/logs


# ============================================
# STAGE 2: Frontend Build
# ============================================
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./

RUN npm config set registry https://registry.npmmirror.com && \
    npm install --no-audit --progress=false || npm install --no-audit --progress=false

COPY frontend/ ./

RUN npx ng build --configuration production


# ============================================
# STAGE 3: Runtime (NGINX + FASTAPI)
# ============================================
FROM python:3.11-slim

# Install only essential packages (no gcc/g++)
RUN apt-get update && apt-get install -y \
    nginx supervisor curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Backend copy
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin
COPY --from=backend /backend /app

# Frontend copy
COPY --from=frontend-builder /frontend/dist/frontend/browser /var/www/html

# ============================================
# NGINX CONFIG
# ============================================
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /var/www/html; \
    index index.html; \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    location /api/ { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
    } \
}' > /etc/nginx/sites-available/default

RUN rm -f /etc/nginx/sites-enabled/default && \
    ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/ && \
    rm -f /etc/nginx/conf.d/default.conf && \
    nginx -t

RUN echo '[supervisord]\nnodaemon=true\n\
[program:backend]\ncommand=uvicorn app.main:app --host 0.0.0.0 --port 8000\ndirectory=/app\nautorestart=true\n\
[program:nginx]\ncommand=nginx -g "daemon off;"\nautorestart=true' \
> /etc/supervisor/conf.d/app.conf

EXPOSE 80 8000

CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]