# quickshare

Share notebooks via Jupyter widgets in Sagemaker notebooks

![](https://i.postimg.cc/ZYGrY4Xq/quickshare-highlights.png)

### Setup and Installation

Install Jupyter widgets in Sagemaker notebooks via notebook lifecycle config

    #!/bin/bash
    set -e

    # OVERVIEW
    # This script installs a jupyterlab extension package in SageMaker Notebook Instance

    sudo -u ec2-user -i <<'EOF'
    source /home/ec2-user/anaconda3/bin/activate JupyterSystemEnv
    jupyter labextension install @jupyter-widgets/jupyterlab-manager
    source /home/ec2-user/anaconda3/bin/deactivate

    source /home/ec2-user/anaconda3/bin/activate python3
    pip install quickshare
    source /home/ec2-user/anaconda3/bin/deactivate
    EOF
    
Installation (from notebook cell)

    pip install quickshare

### Develop
- [Package module](https://marthall.github.io/blog/how-to-package-a-python-app/) - `python setup.py sdist`
- [Upload to pypi using twine](https://stackoverflow.com/a/58972772/3800324) - `python -m twine...`
