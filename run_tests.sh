# This script runs the same commands as ./github/workflows/ci.yml
# Intended for local use only

pylint $(git ls-files '*.py')

flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

mypy $(git ls-files '*.py')

pytest --cov src tests/
