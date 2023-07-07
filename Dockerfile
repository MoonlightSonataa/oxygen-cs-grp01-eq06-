## To implement
# Dockerfile
FROM python:3

WORKDIR /usr/src/app

COPY . .
USER root
RUN pip install pipenv --user
RUN pipenv install


CMD [ "pipenv run", "start" ]