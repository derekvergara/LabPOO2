from setuptools import find_packages, setup

setup(
    name="pipeline_covid",
    packages=find_packages(exclude=["pipeline_covid_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
