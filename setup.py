# setup.py

from setuptools import setup, find_packages

setup(
    name='smartfan',
    version='0.0.1',
    description='A sample Python project with CLI and importable module',
    author='Ivan Cenov',
    author_email='i_cenov@botevgrad.com',
    url='https://github.com/jwalkerbg/cliapp',  # Project's GitHub or website
    packages=find_packages(),
    install_requires=[
        'jsonschema',  # Add your dependencies here
        'mqttms'
    ],
    entry_points={
        'console_scripts': [
            'smartfan=smartfan.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update with your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify the minimum Python version
)
