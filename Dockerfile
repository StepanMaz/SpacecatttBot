FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./

CMD ["python", "./main.py"]

# docker run -d --name SpacecatttBot --env-file .env bot