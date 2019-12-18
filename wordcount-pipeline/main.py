from __future__ import absolute_import

import logging
import datetime
import argparse
import logging
import re

from past.builtins import unicode

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

from word_extracting_dofn import WordExtractingDoFn

def format_result(word_count):
  (word, count) = word_count
  return '%s: %s' % (word, count)

def run(argv=None):
  """Main entry point; defines and runs the wordcount pipeline."""

  parser = argparse.ArgumentParser()
  parser.add_argument('--input',
                      dest='input',
                      default='gs://dataflow-samples/shakespeare/kinglear.txt',
                      help='Input file to process.')

  parser.add_argument('--output',
                      dest='output',
                      required=True,
                      help='Output GCS file path to write results to.')
  
  known_args, pipeline_args = parser.parse_known_args(argv)

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = False

  
  # Pipeline instantiated without the `with` to be able to 
  # submit it and terminate the HTTP request, without having
  # to wait for the pipeline to finish
  pipeline = beam.Pipeline(options=pipeline_options)
  ( pipeline
    | 'Read' >> ReadFromText(known_args.input)
    | 'ExtractWords' >> beam.ParDo(WordExtractingDoFn())
    | 'PairWithOne' >> beam.Map(lambda x: (x, 1))
    | 'GroupAndSum' >> beam.CombinePerKey(sum)
    | 'Format' >> beam.Map(format_result)
    | 'Write' >> WriteToText(known_args.output)
  )    

  logging.info("Will run the pipeline")
  pipeline.run()
  logging.info("Pipeline submitted. Terminating")
    


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()