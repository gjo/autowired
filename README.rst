=========================================
autowired - auto wire utilities for wired
=========================================


Development
-----------

Install runtime and dependencies::

  $ PIPENV_VENV_IN_PROJECT=1 pipenv --python /path/to/python3.7
  $ pipenv install --dev


Run tests::

  $ PATH=/path/to/python3.4:/path/to/python3.5:/path/to/python3.6:/path/to/pypy3:$PATH pipenv run tox


Update depedencies::

  $ pipenv update --dev
  $ pipenv run invoke lock-constraints
  $ pipenv run tox -r

