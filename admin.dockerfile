FROM python:3

RUN mkdir -p /opt/src/applications/admin
WORKDIR /opt/src/applications/admin

COPY applications/admin/application.py ./application.py
COPY applications/admin/adminDecorator.py ./adminDecorator.py
WORKDIR /opt/src/applications
COPY applications/configuration.py ./configuration.py
COPY applications/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/"
WORKDIR /opt/src/applications/admin

ENTRYPOINT ["python","application.py"]