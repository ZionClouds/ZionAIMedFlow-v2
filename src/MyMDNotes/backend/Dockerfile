FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "3"]