rm -rf dist
pip uninstall dpsiw -y
python -m build
pip install -e .
dpsiw ui
