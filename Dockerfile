FROM python:3-alpine

ADD src src

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV FLASK_APP=src/app.py

EXPOSE 5000

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]