from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="abaco_core",
    version="0.1.0",
    author="Abaco Capital",
    author_email="jeninefer@abacocapital.co",
    description="A library for financial calculations and KPI analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jeninefer/Commercial-View",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
    ],
)
