FROM python:3-alpine

ADD src app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]