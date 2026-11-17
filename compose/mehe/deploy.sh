#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
env_file=${MEHE_ENV_FILE:-.env.mehe}
if [ ! -r "$env_file" ]; then
    echo "Copy env.mehe.example to .env.mehe and fill the deployment values first." >&2
    exit 1
fi
compose() { docker compose --env-file "$env_file" -f compose.mehe.yml "$@"; }
value() {
    awk -v key="$1" 'index($0,key "=")==1 {sub(/^[^=]*=/,""); sub(/\r$/,""); if ($0 ~ /^".*"$/ || $0 ~ /^\047.*\047$/) {$0=substr($0,2,length($0)-2)}; print; exit}' "$env_file"
}
preflight() {
    compose config --quiet
    share=$(value NFE_FILE_SHARE_HOST_PATH)
    cert=$(value MEHE_TLS_CERT_FILE)
    key=$(value MEHE_TLS_KEY_FILE)
    host=$(value MEHE_HOST)
    [ -n "$share" ] && mountpoint -q "$share" || { echo "Mount the actual MEHE share on NFE_FILE_SHARE_HOST_PATH first." >&2; exit 1; }
    [ -r "$cert" ] && [ -r "$key" ] || { echo "Install the configured HTTPS certificate and private-key files first." >&2; exit 1; }
    openssl x509 -in "$cert" -noout -checkend 0
    case "$host" in
        *[!0-9.]* ) openssl x509 -in "$cert" -noout -checkhost "$host" ;;
        * ) openssl x509 -in "$cert" -noout -checkip "$host" ;;
    esac
    compose run --rm --no-deps django python manage.py check --deploy
}
case "${1:-status}" in
    preflight) preflight ;;
    prepare)
        preflight
        compose run --rm --no-deps django python manage.py migrate --noinput
        compose run --rm --no-deps django python manage.py collectstatic --noinput
        compose run --rm --no-deps django python manage.py datasync_photo_storage_check --require-share --write-test
        ;;
    up) preflight; compose up -d --wait ;;
    token) compose run --rm --no-deps django python manage.py datasync_create_client --username compiler-local ;;
    admin) compose run --rm --no-deps django python manage.py createsuperuser ;;
    status) compose ps ;;
    logs) compose logs --tail 100 -f ;;
    down) compose down ;;
    *) echo "Usage: sh compose/mehe/deploy.sh {preflight|prepare|up|token|admin|status|logs|down}" >&2; exit 2 ;;
esac
