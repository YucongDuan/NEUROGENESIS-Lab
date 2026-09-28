# Run NEUROGENESIS Lab

[Online project home](https://yucongduan.github.io/NEUROGENESIS-Lab/) · [Versioned downloads](https://github.com/YucongDuan/NEUROGENESIS-Lab/releases/tag/v1.0.0) · [中文](README.zh-CN.md)

1. Download the versioned ZIP or clone this repository and open its project directory.
2. Use Python 3.10 or later. The source application has no third-party runtime dependencies.
3. Run the following commands in that directory:

```bash
python run.py list
python run.py run hh --out runs/my-hh
python run.py replay runs/my-hh
python run.py serve --port 8766
```

Open `http://127.0.0.1:8766` to use the local workbench. Stop it with Ctrl+C. The online GitHub Pages site serves the supplied result reports; it does not run the Python server or accept research data.

To use the packaged distribution, create an isolated Python environment and install the wheel from the release with `python -m pip install --no-deps <downloaded-wheel.whl>`. The `neurogenesis` command is then available.

```bash
python -m unittest discover -s tests -v
python tools/verify_release.py
```

Read [the original guide](docs/USER_GUIDE.md) and [the English handbook](docs/NEUROGENESIS_Lab_English_Handbook.docx) for input formats, examples and model limitations. Do not overwrite supplied reference results when creating your own runs.
