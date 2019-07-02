FROM tiangolo/uwsgi-nginx-flask:python3.7

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV UWSGI_CHEAPER 4
ENV UWSGI_PROCESSES 16
ENV NGINX_WORKER_PROCESSES 12
ENV LISTEN_PORT 5555
ENV STATIC_PATH "/app/app/static"

EXPOSE 5555:5555

COPY ./app /app
