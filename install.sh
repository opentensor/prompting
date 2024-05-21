#!/bin/bash

# Uninstalling mathgenerator
pip uninstall mathgenerator -y

# Install npm 
apt update
apt install npm -y

# Install pm2 globally
npm install -g pm2

# Installing package from the current directory
pip install -e .
