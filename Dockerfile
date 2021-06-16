FROM python:3.9-alpine

COPY requirements.txt /requirements.txt
COPY entrypoint.py /entrypoint.py

RUN pip install -r /requirements.txt

CMD ["/entrypoint.py"]
ENTRYPOINT ["python"]
