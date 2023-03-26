#!/usr/bin/env bash
cd /app
echo 'Performing DB Migrations'
flask db upgrade

echo 'Fixing OSP Permissions Post Migration'
chown -R www-data:www-data /app

export OSP_CORE_TYPE

echo "Starting OSP-$OSP_CORE_TYPE"
case "$OSP_CORE_TYPE" in
 celery) supervisord --nodaemon --configuration /app/docker-files.d/supervisord-celery.conf ;;
 beat) supervisord --nodaemon --configuration /app/docker-files.d/supervisord-celery-beat.conf ;;
    *) supervisord --nodaemon --configuration /app/docker-files.d/supervisord.conf ;;
esac