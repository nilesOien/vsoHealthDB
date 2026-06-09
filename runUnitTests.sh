#!/bin/bash

source pyEnv/bin/activate
export PYTHONPATH="`pwd`"
pytest -v

exit 0

