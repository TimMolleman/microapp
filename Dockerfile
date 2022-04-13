FROM python:3.8-slim-buster

# Copy needed files
COPY /src/worker /app
COPY /src/helpers /app/helpers
COPY /src/cosmos_db /app/cosmos_db
COPY worker_requirements.txt /app/requirements.txt
WORKDIR /app

# Apt-get install cmake, which is needed for the uamqp python package
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    cmake

# Install the requirementst into the docker
RUN pip install -r requirements.txt

CMD ["python", "./worker.py"]