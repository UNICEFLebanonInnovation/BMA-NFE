FROM python:3.10-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV SSH_PASSWD="root:Docker!"

# Install build tools before Python packages, and stop on package failures.
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get -o Acquire::Retries=3 update && \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl && \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
        openssh-server --option=Dpkg::Options::="--force-confdef" \
                       --option=Dpkg::Options::="--force-confold" \
                       --option=Dpkg::Options::="--force-overwrite" && \
    echo "$SSH_PASSWD" | chpasswd && \
    mkdir -p /var/run/sshd /root/.ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./compose/django/sshd_config /etc/ssh/sshd_config

WORKDIR /code/

ARG REQUIREMENTS_FILE=production.txt
COPY requirements /code/requirements
RUN pip install --no-cache-dir --timeout 120 --retries 5 -r /code/requirements/$REQUIREMENTS_FILE

COPY . /code/

# Windows checkouts may contain CRLF shell scripts; Linux entrypoints need LF.
RUN find /code/compose -type f -name '*.sh' -exec sed -i 's/\r$//' {} + -exec chmod +x {} +

RUN python manage.py collectstatic --noinput --settings=config.settings.test

EXPOSE 2222 80

ENTRYPOINT ["/code/compose/django/entrypoint.sh"]
CMD ["/code/compose/django/gunicorn.sh"]
