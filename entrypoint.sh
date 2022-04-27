#!/usr/bin/env bash
cd /app
python3 manage.py db upgrade
python3 app.py