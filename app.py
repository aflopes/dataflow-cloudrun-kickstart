import os
import json
import subprocess
from logging.config import dictConfig

from datetime import datetime
from flask import Flask, request, Response

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
log = app.logger
Response.default_mimetype = 'application/json'

@app.route('/env', methods=['GET'])
def env():
    return Response(json.dumps(dict(os.environ), indent=4))

@app.route('/', methods=['POST'])
def kickstart():
    
    request_json = request.get_json(silent=True)

    request_json = request.get_json(silent=True)
    if not request_json: 
        request_json = dict()
    
    runner = request_json.get('runner')
    if (runner == None):
        return Response("no runner specified", status=400) 

    output = request_json.get('output')
    if (output == None):
        return Response("no output specified", status=400)
    
    region = request_json.get('region')
    if (region == None):
        return Response("no region specified", status=400)

    project = request_json.get('project')
    if (project == None):
        return Response("no project specified", status=400)

    bucket = request_json.get('bucket')
    if (project == None):
        return Response("no bucket specified", status=400)

    job_name = request_json.get('job_name', 'cloudrun-started-wordcount-job')    

    log.info(f'Kickstarting pipeline on {runner}')
    stream_out = execute_pipeline('gs://dataflow-samples/shakespeare/kinglear.txt', output, runner, region, project, job_name, bucket)

    return Response(stream_out, mimetype='text/plain')


def execute_pipeline(input_file, output, runner, region, project, job_name, bucket):
    command = [
        'python', 
        'wordcount-pipeline/main.py' ,
        f'--runner={runner}',
        f'--input={input_file}',
        f'--output={output}',
        f'--job_name={job_name}',
        f'--region={region}',
        f'--project={project}',
        f'--temp_location={bucket}/temp',
        f'--staging_location={bucket}/staging',
        '--extra_package=dist/wordcount-extras-0.0.1.tar.gz',
        '--setup_file=wordcount-pipeline/setup.py',
    ]
    return execute_and_log_command(command)

def execute_and_log_command(command_array, cwd='./'):
    log.info(f"Executing {' '.join(command_array)}")
    proc = subprocess.Popen(command_array, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while proc.poll() is None:
        line = proc.stdout.readline().decode('utf-8').rstrip()
        log.info(line)
        yield line + '\n'

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
