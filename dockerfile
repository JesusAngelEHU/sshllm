FROM python:3.11-slim

WORKDIR /app

COPY dist/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dist/ .

EXPOSE 22

CMD ["python", "main.py"]