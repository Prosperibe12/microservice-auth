ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install os dependencies for our mini vm
RUN apt-get update \ 
    && apt-get install -y --no-install-recommends --no-install-suggests \ 
    build-essential default-libmysqlclient-dev libpq-dev pkg-config \ 
    && pip install --no-cache-dir --upgrade pip

# Set the working directory to that same code directory
WORKDIR /app

# Copy the requirements file into the container
COPY ./requirements.txt /app

# Install the Python project requirements
RUN pip install --no-cache-dir -r /app/requirements.txt 

# Copy the rest of the code
COPY . /app

# Set the Django default project name
ARG PROJ_NAME="project_core"

# Create a bash script to run the Django project
# This script will execute at runtime when
# the container starts and the database is available
RUN printf "#!/bin/bash\n" > ./runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n\n" >> ./runner.sh && \
    printf "python manage.py makemigrations --no-input\n" >> ./runner.sh && \
    printf "python manage.py migrate --no-input\n" >> ./runner.sh && \
    printf "gunicorn ${PROJ_NAME}.wsgi:application --bind \"0.0.0.0:\$RUN_PORT\" &\n" >> ./runner.sh && \
    printf "celery -A ${PROJ_NAME} worker --pool=solo -l INFO\n" >> ./runner.sh

# Make the bash script executable
RUN chmod +x runner.sh

# Clean up apt cache to reduce image size
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose port 8000
EXPOSE 8000

# Run the Django project via the runtime script
# when the container starts
CMD ["./runner.sh"]