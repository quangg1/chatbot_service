# start.sh
#!/bin/sh

# Activate virtual environment if exists
if [ -d "venv" ]; then
    . venv/bin/activate
fi

# Start the application using uvicorn
exec uvicorn src.main:app --host 0.0.0.0 --port $PORT