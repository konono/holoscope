#!/usr/bin/env bash

PROJECT_DIR='../../holoscope'

if [ -d build ]; then
  rm -rf build
fi

# Recreate build directory
mkdir -p build/function/ build/layer/

# Copy source files
echo "Copy source files"
cp -p ../../config.toml build/function/
cp -p ../../run.py build/function/


# Pack python libraries
echo "Pack python libraries"
pipenv run pip3 install -r ../../requirements.txt -t ./build/layer/python/
cp -r $PROJECT_DIR ./build/layer/python/

# Remove pycache in build directory
find build -type f | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm

