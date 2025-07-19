# Multi-stage build: Streamlit app + Nginx reverse proxy
FROM python:3.11-slim as builder
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# --- Final image with Nginx and Streamlit ---
FROM python:3.11-slim
WORKDIR /app

# Install Nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copy app and dependencies
COPY --from=builder /app /app
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80

# Start Nginx and Streamlit
CMD ["sh", "-c", "streamlit run app.py --server.address=127.0.0.1 --server.port=8501 & nginx -g 'daemon off;'"]
