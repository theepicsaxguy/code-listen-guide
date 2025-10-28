#!/bin/bash
# Script to run the FastAPI backend server

cd "$(dirname "$0")"
source ../.venv/bin/activate
PYTHONPATH=/home/develop/code-listen-guide python3 main.py
