import re
import apache_beam as beam

class WordExtractingDoFn(beam.DoFn):

    def process(self, element):
        return re.findall(r'[\w\']+', element.strip(), re.UNICODE)
