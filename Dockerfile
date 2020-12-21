FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY . /app

RUN pip3 install -r /app/requirements.txt
