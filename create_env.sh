#!/bin/bash

virtualenv --no-site-packages --distribute dev_env

. ./dev_env/bin/activate
pip install tornado
pip install pymongo
deactivate
