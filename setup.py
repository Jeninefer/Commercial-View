"""Setup configuration for Commercial-View package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="commercial-view",
    version="0.1.0",
    author="Jeninefer",
    description="Principal KPI analysis for commercial lending",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jeninefer/Commercial-View",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)
