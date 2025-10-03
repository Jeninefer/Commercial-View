from setuptools import setup, find_packages

setup(
    name="commercial-view",
    version="0.1.0",
    description="Principal KPI Analysis",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    python_requires=">=3.7",
)
