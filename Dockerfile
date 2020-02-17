FROM ubuntu:18.04

COPY . /home/simple_order
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev
RUN python3 -m pip install --upgrade -r /home/simple_order/requirements.txt

WORKDIR /home/simple_order
RUN python3 setup.py install