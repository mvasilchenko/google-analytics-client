from setuptools import setup, find_packages

setup(
    name="google-analytics-client",
    version="0.1.0",
    url="https://github.com/mvasilchenko/google-analytics-client",
    license="MIT",
    author="Mikhail Vasilchenko",
    author_email="rekoy88@gmail.com",
    description="",
    packages=find_packages(exclude=['tests']),
    load_description=open("README.md").read(),
    zip_safe=False,
)
