#!/bin/bash

source pyEnv/bin/activate
export PYTHONPATH="$HOME/vsoHealthDB"
pytest -v

exit 0

