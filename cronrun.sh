#!/bin/bash
cd $1
source $1/.venv/bin/activate
export $(cat .env | xargs)
python -m app.SberCatClient