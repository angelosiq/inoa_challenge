FROM python:3.11.0-slim

ENV PYTHONUNBUFFERED 1
ENV TZ 'America/Sao_Paulo'

WORKDIR /project/

ARG EXTRA_ARGS_INSTALL=""

COPY pyproject.toml .
COPY poetry.lock .
COPY README.md .
COPY app ./app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry==1.5.1 && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-cache ${EXTRA_ARGS_INSTALL} && \
    pip uninstall --yes poetry

RUN pip install pipenv && pipenv install ${REQUIREMENTS}

COPY ./docker/utils/wait_for_postgres.py /wait_for_postgres.py
COPY ./docker/utils/entrypoint.sh /entrypoint.sh

EXPOSE 8000

WORKDIR /project/app/

ENTRYPOINT ["/entrypoint.sh"]
