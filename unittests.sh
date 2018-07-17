export PYNUGET_CONFIG_TYPE=TESTING

# If we ran on Windows last, __pycache__ might be setup incorrect.
# Just delete it to make things easier.
rm -r tests/__pycache__
rm -r src/pynuget/__pycache__

pytest -ra --cov-report term-missing --cov pynuget tests/ --durations=5 "$@"

unset PYNUGET_CONFIG_TYPE
