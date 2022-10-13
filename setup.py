import os

from setuptools import setup

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    setup(
        name='query-schema',
        install_requires=['marshmallow', 'marshmallow-sqlalchemy', 'SQLAlchemy'],
        packages=['query_schema'],
        classifiers=[
            'Programming Language :: Python :: 3',
            'Operating System :: OS Independent',
        ],
    )
