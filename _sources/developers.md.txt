# Developer's corner
## Preliminaries

Ensure the needed dependencies are installed in `poetry`:

```bash
poetry install --with test,dev
```

## Package installation (`poetry` + `pip3`)
### Introduction

This section presents two ways to (re)install the package.

* _As a normal user:_ this is the clean approach. But as the runnables are deployed in `~/.local/bin`, you have to update your `PATH` environment variable. To do so, you should to update your `PATH` by adding in the end of your ~/.bashrc` file the following statement, and then restart your `bash`:
```bash
export PATH=${PATH}:${HOME}/.local/bin
```
* _As root:_ as the runnables in `/usr/local/bin`, you don't have to update your variable environment variable.

### Full installation

The first time you install the package, just run one of the following commands.
* As a normal user:
```bash
poetry build
pip3 install dist/*whl
```
* As root:
```bash
poetry build
sudo pip3 install dist/*whl
```

### Full reinstallation

As the package is already install, `pip3` may decide to not redeploy the package. Just use the `--force-reinstall` option. Note that `pip3` will check the package dependencies. This is slow, but required if you have modified the dependencies (in `pyproject.toml`).

* As a normal user:
```bash
poetry build
pip3 install dist/*whl --force-reinstall
```
* As root:
```bash
poetry build
sudo pip3 install dist/*whl --break-system-packages --force-reinstall
```

### Fast reinstallation

Most of time, the dependencies are already deployed and you just want to redeploy the package without checking anything. To do so, use the `--no-deps` option as follows.

* As a normal user:
```bash
poetry build
pip3 install dist/*whl --force-reinstall --no-deps
```
* As root:
```bash
poetry build
sudo pip3 install dist/*whl --break-system-packages --force-reinstall --no-deps
```

## Project dependencies (`poetry`)
### Changing the project dependencies

Open the `pyproject.toml` file and add the needed package in the `[tool.poetry.dependencies]` block. Then, run:
```bash
poetry check
poetry install
poetry lock
```
Do not forget to commit and push the updated `poetry.lock`.

### Analyzing the project depencies

To analyze what is install by `poetry install`, you could run:
```bash
poetry show --tree
```

If you want to check a group optional dependencies (say `--with docs`), run:
```bash
poetry show --tree --with docs
```

You could check the dependencies of your wheels thanks to `pkginfo`:
```bash
pkginfo -f requires_dist dist/*whl
```
## Tests suite (`pytest`)

To launch the test suite, run:

```bash
poetry run pytest
```

## Tests coverage (`coverage`)

_Note:_ You can safely ignore this section as it is unapplicable. Indeed, due to `opencv`, `coverage run -m pytest` cannot produce a good report and so you cannot compute the coverage

To evaluate the test coverage, run:

```bash
poetry run coverage run -m pytest
poetry run coverage xml
```

* Else, with `tox`:
  * The versions of python that are tested are listed in `tox.ini`.
  * To run the tests, run:

```bash
tox -e py
```

## Linter (`flake8`)
### Basic checks

To check the quality of the code, use `flake8`:
```bash
poetry run flake8 src/ tests/
```

### CI checks

The following command reproduce what is done by the continuous integartion (CI) script (see `.gitlab-ci.yml`). Ensure that the following commands successfully pass before running `git push`.
```bash
# Stops the build if there are Python syntax errors or undefined names
poetry run flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
poetry run flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## Documentation (`sphinx`)
### Dependencies

Ensure that all the needed dependencies are intalled in `poetry`:
```bash
poetry install --with docs
```

### With `make`

```bash
poetry run make docs
```

### Without `make`

```bash
poetry run sphinx-apidoc -f -o docs/ src/
poetry run sphinx-build -b html docs/ docs/_build
```

## Publishing a release
### Initialization

1. Create a token in Pypi.

2. Configure this token in your GitHub repository (in the settings tab)
* `PYPI_USERNAME`: `__token__`
* `PYPI_TOKEN`: `pypi-xxxxxxxxxxxx`

3. Configure this token in poetry so that you can use `poetry publish` in the future
```bash
poetry config pypi-token.pypi pypi-xxxxxxxxxxxx
```

### New release

1. Update the changelog `HISTORY.md`, then add and commit this change:

```bash
git add README.md
git commit -m "Updated README.md"
```

2. Increase the version number using `bumpversion`:

```bash
bumpversion patch # Possible values major / minor / patch
git push
git push --tags
```

3. Optionnally, in GitHub, create a release for the tag you have created.
It publishes the package to PyPI (see `.github/workflows/publish_on_pypi.yml`).
Alternatively, you could run:

```bash
poetry publish
```
