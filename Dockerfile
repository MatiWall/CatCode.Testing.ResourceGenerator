FROM python:3.12-slim

ENV POETRY_HOME=/app
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=true

RUN pip install poetry
# Install git in the Docker image
RUN apt-get update && apt-get install -y git
WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-dev

# Install etcd CLI
RUN apt-get update && apt-get install -y curl && \
    curl -L https://github.com/etcd-io/etcd/releases/download/v3.5.0/etcd-v3.5.0-linux-arm64.tar.gz -o etcd.tar.gz && \
    tar xzf etcd.tar.gz && \
    mv etcd-v3.5.0-linux-arm64/etcdctl /usr/local/bin/ && \
    rm -rf etcd.tar.gz etcd-v3.5.0-linux-arm64

COPY . /app

EXPOSE 8000

CMD ["poetry", "run", "python", "main.py"]
