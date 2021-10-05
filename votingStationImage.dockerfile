FROM python:3

RUN mkdir -p /opt/src/applications/votingStation
WORKDIR /opt/src/applications/votingStation

COPY applications/votingStation/application.py ./application.py
COPY applications/votingStation/adminDecorator.py ./adminDecorator.py
WORKDIR /opt/src/applications
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt

RUN mkdir -p /opt/src/applications/daemon
WORKDIR /opt/src/applications/daemon
COPY applications/daemon/application.py ./application.py
WORKDIR /opt/src/applications

RUN pip install -r ./requirements.txt


ENV PYTHONPATH="/opt/src/"
WORKDIR /opt/src/applications/votingStation

ENTRYPOINT ["python","application.py"]