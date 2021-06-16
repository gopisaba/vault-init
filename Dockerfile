FROM python:3.9-alpine

RUN addgroup -S vault && \
    adduser -S -G vault vault

COPY requirements.txt /requirements.txt
COPY entrypoint.py /entrypoint.py

RUN pip install --no-cache-dir -r /requirements.txt

USER vault

CMD ["python", "/entrypoint.py"]
