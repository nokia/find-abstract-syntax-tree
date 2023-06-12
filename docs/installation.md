# Installation
## Linux (Debian / Ubuntu)

Depending on your preferences, you may install the dependencies either through APT or PIP. Please see the following steps if you want to use APT dependencies.
* Install the APT dependencies:

```bash
sudo apt update
sudo apt install git ffmpeg python3 python3-opencv python3-numpy python3-poetry python3-pip python3-tqdm
```

* If you are a developer, please also install the following dependencies:

```bash
sudo apt install python3-pip bumpversion python3-coverage python3-pytest python3-pytest-cov python3-pytest-runner python3-sphinx python3-sphinx-pydata-theme
sudo pip3 install sphinx_mdinclude --break-system-packages
```

## Windows

* Install [poetry](https://pypi.org/project/poetry/).
* Install [anaconda](https://www.anaconda.com/products/distribution) and [ffmpeg](https://ffmpeg.org/download.html).

## Package installation
### From pip

As the package is not released as an open source project, an installation via PIP is not possible.

### From git

* Clone the repository and install the package:

```bash
git clone https://github.com/nokia/find-abstract-syntax-tree.git
cd find-abstract-syntax-tree
```

* Install the missing dependencies and build the wheel of the project:
```
poetry install  # Install the core dependencies. Pass --with docs,test,dev to get the whole set of dependencies.
poetry build    # Build the wheel (see dist/*whl)
```

* Install the wheel you just built, according to one of the following method, that affects the installation scope:
  * _In poetry:_ this imposes to run your python-related commands through `poetry run`.

```bash
poetry run pip3 install dist/*whl
```

  * In a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/): this imposes to run your python-related in the venv.

```bash
python3 -m venv env      # Create your virtual environment
source env/bin/activate  # Activate the "env" virtual environment
which python             # Should be your "env" python interpreter (not /usr/bin/python3)
pip install dist/*whl    # Install your wheel
deactivate               # Leave the  "env" virtual environment
```

  * System-wide (Linux):

```bash
sudo pip3 install dist/*whl --break-system-packages
```

## Get and prepare the input videos

We now prepare the input videos.

* Create the `input/`, `output/`, `remap/` directories in the root directory of the project:

```bash
mkdir input remap output
```

* Download the [input video](https://nokia.sharepoint.com/sites/NokiaArenaInnovationProject766/_layouts/15/stream.aspx?id=%2Fsites%2FNokiaArenaInnovationProject766%2FShared%20Documents%2FGeneral%2Ftest%20material%2FINTERNAL%20MATERIAL%2Finternally%20shared%20material%2FCONFIDENTIAL%5Ftappara%5Filves%5Fclips%2Fraw%20clips%2FNorth%5FGoal%5FCam%2FQ360%5F20220603%5F212625%5F000075%2EMOV) `Q360_20220603_212625_000075.MOV` in the `input/` directory.

* [List the video streams](https://superuser.com/questions/1479702/how-to-list-streams-with-ffmpeg) by using `ffprobe`. It shows that `Q360_20220603_212625_000075.MOV` provides two video streams, namely `0:0` and `0:1`:

```bash
ffprobe -i input/Q360_20220603_212625_000075.MOV
```

* Extract each stream `ffmpeg`. Note that only the front video (`0:0`) is relevant.

```bash
ffmpeg -i input/Q360_20220603_212625_000075.MOV -map 0:0 -c copy input/raw_north_back.mov
ffmpeg -i input/Q360_20220603_212625_000075.MOV -map 0:1 -c copy input/raw_north_front.mov
```

* Remove the [distorsion](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html) introduced by the camera lense:

```bash
python3 remap.py --input input/raw_north_front.mov --output remap/remap_north_front.mp4
```
