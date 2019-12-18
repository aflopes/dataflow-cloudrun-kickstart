# Trigger python Wordcount dataflow batch job with Google Cloud Run

Full example project to trigger a python wordcount Dataflow batch job with an extra package, using a Google Cloud Run service endpoint.

## Requirements

* Have a GCP project with the following services active
    * Dataflow
    * Cloud Run
    * Cloud Build
    * Container Registry
* Have gcloud SDK installed (https://cloud.google.com/sdk/install)

## Components

### Flask Application

The web application that is deployed in Google Cloud Run.

When the `POST /` endpoint is called with the proper JSON body (see example below), it starts a `subprocess` that executes the Apache Beam pipeline defined in [wordcount-pipeline/main.py](wordcount-pipeline/main.py)

### wordcount-pipeline

The Apache Beam application that implements the wordcount batch job pipeline.

### wordcount-extras

An extra package to contain the dependencies required by the wordcount-pipeline. 

In this example it only contains the `DoFn` `WordExtractingDoFn` but it can contain any code dependency that is not available in PyPi.

This module distribution package is created in the [docker build](Dockerfile) and copied into the service docker image

## Build
```bash
gcloud builds submit \
    --tag gcr.io/<your-gcp-project>/dataflow-kick 
    --region <your-prefered-region> \
    --project <your-gcp-project>
```

## Deploy
```bash
gcloud run deploy dataflow-kick \
    --image gcr.io/<your-gcp-project>/dataflow-kick \
    --platform managed \
    --memory 1024M \
    --region <your-prefered-region> \
    --project <your-gcp-project>
```

## Submit dataflow wordcount pipeline
```bash
curl -X POST $(gcloud run services list --project <your-gcp-project> --platform managed --filter=metadata.name:dataflow-kick --format="table[no-heading](status.url)") \
    -H "Authorization: Bearer $(gcloud auth print-identity-token) --project <your-gcp-project>" \
    -H "Content-Type:application/json" \
    -d '
{
    "runner": "DataflowRunner",
    "output": "gs://<your-output-bucket>/wordcount-output",
    "region": "<your-prefered-region>",
    "project": "<your-gcp-project>",
    "staging_bucket": "gs://<bucket for staging>",
    "temp_bucket": "gs://<bucket for temp>",
    "job_name": "wordcound"
}'
```

## Get Python runtime environment variables
```bash
curl -X GET $(gcloud run services list --project <your-gcp-project> --platform managed --filter=metadata.name:dataflow-kick --format="table[no-heading](status.url)")/env \
    -H "Authorization: Bearer $(gcloud auth print-identity-token --project <your-gcp-project>)"
```

