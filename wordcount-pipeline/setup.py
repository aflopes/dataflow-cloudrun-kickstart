from setuptools import setuptools, find_packages

setuptools.setup(
    name="wordcount-pipeline",
    version="0.0.1",
    description="Word Count Pipeline",
    packages=find_packages(),
    install_requires=["wordcount-extras", "apache-beam[gcp]"],
)

