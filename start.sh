#!/bin/bash
if [ -z "$1" ]; then
  port=8501
else
  port="$1"
fi
echo "Streamlit starting on port $port..."
streamlit run --server.port "$port" app.py
echo "Closed."