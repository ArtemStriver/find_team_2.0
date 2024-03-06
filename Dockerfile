FROM python:3.10

RUN mkdir /find_team

WORKDIR /find_team

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN mkdir certs

RUN openssl genrsa -out certs/jwt-private.pem 2048
RUN openssl rsa -in certs/jwt-private.pem -outform PEM -pubout -out certs/jwt-public.pem


RUN chmod a+x docker/*.sh
