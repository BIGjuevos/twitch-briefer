FROM tiangolo/uwsgi-nginx-flask:python3.7

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV UWSGI_CHEAPER 16
ENV UWSGI_PROCESSES 64
ENV NGINX_WORKER_PROCESSES 8
ENV LISTEN_PORT 5555

EXPOSE 5555:5555

COPY ./app /app
