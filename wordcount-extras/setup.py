from setuptools import setuptools, find_packages

setuptools.setup(
    name="wordcount-extras",
    version="0.0.1",
    description="Word Count Extra Packages",
    packages=find_packages(),
    install_requires=["apache-beam"],
)
