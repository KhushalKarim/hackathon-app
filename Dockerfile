FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set a writable Streamlit config directory
ENV STREAMLIT_CONFIG_DIR="/app/.streamlit"

# Create the directory and default config
RUN mkdir -p /app/.streamlit && \
    echo "[server]\nheadless = true\nport = 8501\nenableCORS = false\n" > /app/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
