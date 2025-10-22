FROM python:3.11-bookworm

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_HTTP_TIMEOUT=120

WORKDIR /app

# Install dependencies required for Pillow, psycopg2, etc.
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff5-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy UV binary from Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy requirements
COPY alpha_pms/requirements.txt .

# Install Python dependencies
RUN uv pip install -r requirements.txt --system

# Copy the rest of your app
#COPY alpha_pms/ .

EXPOSE 8000

#make entrypoint executable
RUN chmod +x /entrypoint.prod.sh

CMD ["./entrypoint.prod.sh"]
