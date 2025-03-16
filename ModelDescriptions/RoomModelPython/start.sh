#!/bin/bash
while ! command -v code &> /dev/null; do
    echo "Waiting for VS Code to be available..."
    sleep 2
done

echo "VS Code is ready, installing extensions..."
code --install-extension ms-python.python
