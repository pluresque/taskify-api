FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

WORKDIR /
COPY . .

# This is to prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# This is to prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Set the working directory
ENV PYTHONPATH $PWD/src

# Install dependencies
RUN pip install --no-cache-dir -e .

# Make the entrypoint script executable
RUN chmod +x /src/scripts/docker-entrypoint.sh

ENTRYPOINT ["/bin/sh", "src/scripts/docker-entrypoint.sh"]