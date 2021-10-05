FROM python:3

RUN mkdir -p /opt/src/applications/daemon
WORKDIR /opt/src/applications/daemon

COPY applications/daemon/application.py ./application.py
WORKDIR /opt/src/applications
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/"
WORKDIR /opt/src/applications/daemon

ENTRYPOINT ["python","application.py"]