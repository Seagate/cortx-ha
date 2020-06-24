import os
from setuptools import setup, find_packages


def get_version():
    ver = os.environ.get('PCS_CLIENT_VERSION')
    if ver:
        return ver
    with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
        return f.read().rstrip('\n')


setup(
    name='pcswrap',
    version=get_version(),
    packages=find_packages(),
    setup_requires=['flake8', 'mypy', 'pkgconfig'],
    entry_points={'console_scripts': ['pcswrap=pcswrap.client:main']},
)
