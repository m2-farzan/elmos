FROM python:3.9

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 80

CMD [ "python", "main.py" ]
