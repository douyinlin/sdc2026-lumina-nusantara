#!/bin/sh
# Replit's Nix Python is immutable; install only into the project-local prefix.
set -eu
cd "$(dirname "$0")/.."
python_version="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
python -m pip install --upgrade --target ".pythonlibs/lib/python${python_version}/site-packages" -r requirements.txt
