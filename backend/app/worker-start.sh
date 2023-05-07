#! /usr/bin/env bash
set -e

(cd /app; poetry install)
python /app/app/celeryworker_pre_start.py

celery -A app.worker.celery_app worker -l info -Q main-queue -c 1
