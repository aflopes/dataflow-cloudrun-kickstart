# Stage 0: Create extra packages distributions
FROM python:3.7-slim

WORKDIR /src
COPY ./wordcount-extras ./wordcount-extras
RUN python ./wordcount-extras/setup.py sdist


# Stage 1: Create runtime image
FROM python:3.7-slim

ENV APP_HOME /app

WORKDIR $APP_HOME
COPY . ./

#Copy extra package from stage 0
COPY --from=0 /src/dist ./dist

# Install production dependencies.
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install gunicorn \
    && pip install -r requirements.txt 

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
