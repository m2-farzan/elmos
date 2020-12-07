FROM ubuntu:20.04

MAINTAINER Mostafa Farzan "m2_farzan@yahoo.com"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev apache2 libapache2-mod-wsgi-py3 libmariadb-dev-compat

# FOR STATIC IMAGE:
# COPY . /var/www/elmos
# WORKDIR /var/www/elmos

# FOR FASTER DEV:
WORKDIR /
COPY ./requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt

COPY ./apache.conf /etc/apache2/sites-available/001-elmos.conf
RUN a2ensite 001-elmos.conf
RUN a2dissite 000-default.conf
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

EXPOSE 80
CMD ["apachectl", "-D", "FOREGROUND"]
