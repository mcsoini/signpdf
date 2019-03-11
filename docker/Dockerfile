FROM python:3.6-slim

RUN apt-get update && apt-get install -y bash libpq-dev gcc tree

USER root
# set time zone to prevent ImageMagick from prompting
ADD install_tzdata.sh /signpdf/setup/install_tzdata.sh
RUN chmod +x /signpdf/setup/install_tzdata.sh
RUN /signpdf/setup/install_tzdata.sh

RUN apt-get install -y imagemagick

# fix ImageMagick policy settings so we can actually write gifs
ADD policy.xml /etc/ImageMagick-6/policy.xml



COPY requirements.txt /signpdf/requirements.txt
WORKDIR /signpdf
RUN pip install -r requirements.txt

RUN mkdir /signpdf/app/static/signature -p
RUN mkdir /signpdf/app/static/numbers -p
RUN mkdir /signpdf/app/static/numbers2 -p

RUN mkdir /signpdf/app/static/temp -p

WORKDIR /signpdf

