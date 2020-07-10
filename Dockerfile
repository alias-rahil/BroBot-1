FROM python:3
COPY . .

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y openssh-server

CMD [ "python3", "index.py" ]
