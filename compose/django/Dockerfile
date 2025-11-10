FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV SSH_PASSWD="root:Docker!"

# Pre-install tools and openssh-server but disable triggers/postinst
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl && \
    apt-get install -y --no-install-recommends \
        openssh-server --option=Dpkg::Options::="--force-confdef" \
                       --option=Dpkg::Options::="--force-confold" \
                       --option=Dpkg::Options::="--force-overwrite" || true && \
    echo "$SSH_PASSWD" | chpasswd && \
    mkdir -p /var/run/sshd /root/.ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./compose/django/sshd_config /etc/ssh/sshd_config

WORKDIR /code/

ARG REQUIREMENTS_FILE=production.txt
COPY requirements /code/requirements
RUN pip install --no-cache-dir -r /code/requirements/$REQUIREMENTS_FILE

COPY . /code/

RUN python manage.py collectstatic --noinput --settings=config.settings.test

EXPOSE 2222 80

ENTRYPOINT ["/code/compose/django/entrypoint.sh"]
CMD ["/code/compose/django/gunicorn.sh"]
