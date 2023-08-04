## To implement
# Dockerfile
# FROM python
FROM fsfe/pipenv:bitnami-3.8

WORKDIR /usr/src/app

COPY . .
RUN pip install psycopg2-binary
RUN pip install -r requirements.txt
# USER root
# RUN pip install pipenv --user
# RUN pipenv --version

# Install pipenv and compilation dependencies
# RUN pip install pipenv
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
#COPY Pipfile .
#COPY Pipfile.lock .
# RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
# RUN pipenv install

# RUN pipenv run start
# ENTRYPOINT ["python", "-m", "pipenv", "run"]
# CMD ["start"]


# CMD [ "pipenv run", "start" ]
# CMD [ "pip", "start" ]
CMD ["pipenv", "run", "python", "src/main.py"]