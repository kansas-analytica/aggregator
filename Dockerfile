FROM ubuntu:latest
MAINTAINER Patrick Canny "therealcans@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
ADD . /flask-app
WORKDIR flask-app
RUN make build
ENTRYPOINT ["python"]
CMD ["main.py"]
