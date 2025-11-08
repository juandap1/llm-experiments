FROM python:3.10-slim

WORKDIR /app

# Copy dependencies first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY ./src ./src

ENV FLASK_APP=src/server.py
ENV FLASK_ENV=development
ENV PYTHONPATH=/app
ENV FLASK_DEBUG=1

EXPOSE 3141

CMD ["flask", "run", "--host=0.0.0.0", "--port=3141"]
