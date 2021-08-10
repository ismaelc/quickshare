from distutils.core import setup

#with open('./quickshare/requirements.txt') as f:
#    requirements = f.read().splitlines()

setup(
    name='quickshare',
    version='0.2',
    packages=['quickshare'],
    #install_requires=requirements,
    install_requires=[
        'ipywidgets',
        'ipython'
    ]
)