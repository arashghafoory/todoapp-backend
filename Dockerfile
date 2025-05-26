FROM python:3.11-slim

WORKDIR /app

ARG PORT=5000
ENV PORT=${PORT}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${PORT}

CMD ["python", "app.py"]
