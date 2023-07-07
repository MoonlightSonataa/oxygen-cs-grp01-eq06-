## To implement
# Dockerfile
FROM python:3

WORKDIR /usr/src/app

COPY . .
USER root
RUN pip install pipenv --user
# Install pipenv and compilation dependencies
# RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
RUN pipenv install


CMD [ "pipenv run", "start" ]