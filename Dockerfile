FROM python:3.11-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY research_agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project
COPY research_agent ./research_agent

# Build Frontend
WORKDIR /app/research_agent/frontend
RUN npm install
RUN npm run build

# Move index.html to templates
# Vite outputs to ../web_app/static/web_app (configured below), so index.html is at ../web_app/static/web_app/index.html
# We move it to ../web_app/templates/web_app/index.html
RUN mv ../web_app/static/web_app/index.html ../web_app/templates/web_app/index.html

# Back to Django Project Root
WORKDIR /app/research_agent

CMD ["python", "manage.py", "runserver", "0.0.0.0:8009"]
