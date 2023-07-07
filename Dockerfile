## To implement
# Dockerfile
FROM python:3

WORKDIR /usr/src/app

COPY . .
RUN pipenv install


CMD [ "pipenv run", "start" ]