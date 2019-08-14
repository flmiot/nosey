import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nosey",
    version="0.0.1",
    author="Florian Otte",
    author_email="",
    description="A lightweight pure-Python X-ray emission analysis package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flmiot/nosey",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
