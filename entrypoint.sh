#!/usr/bin/env bash
cd /app
flask db upgrade
python3 app.py