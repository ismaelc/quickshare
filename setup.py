from distutils.core import setup

with open('./quickshare/requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='quickshare',
    version='0.1',
    packages=['quickshare'],
    install_requires=requirements,
)