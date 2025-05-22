FROM python:3.10-alpine

WORKDIR /srv

COPY ../../requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD python3 synchronizer.py