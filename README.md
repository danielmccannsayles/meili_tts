### Actual App now

Run this from main/

```bash
pyinstaller launch.spec
```

Then copy the launch exec into .app/contents/MacOS
And make sure Resources/ is at the same level

### Old documentation

To create the launch.spec I ran:

```bash
pyinstaller --onefile \
  --add-data "Resources:Resources" \
  --hidden-import=flask \
  --hidden-import=fitz \
  --hidden-import=numpy \
  --hidden-import=soundfile \
  --hidden-import=kokoro \
  --hidden-import=rumps \
  launch.py
```

### How to run

Run the ipynb file. It will produce things

### Serve

```bash
python3 -m http.server 8000
```

## Requirements

- pip install reqirements.txt
- Uses [Kokoro](https://github.com/hexgrad/kokoro?tab=readme-ov-file), so need espeak-ng

_Note: Only works on mac rn (I assume)_
