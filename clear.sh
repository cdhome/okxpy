#!/bin/bash
find . -name '__pycache__' -type d -exec rm -rf {} \;
find . -name '.DS_Store' -type f -delete
find . -name "._*" -delete
