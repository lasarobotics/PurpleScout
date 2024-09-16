FROM python:3-slim-bookworm
LABEL org.opencontainers.image.source="https://github.com/lasarobotics/PurpleScout"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt .
COPY *.py .
RUN mkdir templates/
COPY templates/ templates/
RUN mkdir static/
COPY static/ static/
RUN mkdir data/
RUN pip3 install -r requirements.txt
#RUN pip3 install werkzeug==2.1.2 && pip3 install flask && pip3 install flask-socketio && pip3 install flask-wtf && pip3 install tbapy
#RUN pip3 install flask && pip3 install flask-socketio==5.2.0 && pip3 install flask-wtf && pip3 install tbapy
EXPOSE 5000
CMD [ "python", "./main.py" ]
