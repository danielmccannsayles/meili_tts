### Actual App now

Run this from main/

```bash
pyinstaller launch.spec
```

Then copy the launch exec into MeiliTTS.app/contents/MacOS
And make sure Resources/ is at the same level

### DMG

```bash
create-dmg \
  --volname "MeiliTTS" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "MeiliTTs.app" 175 120 \
  --hide-extension "MeiliTTs.app" \
  --app-drop-link 425 120 \
  "MeiliTTs.dmg" \
  "MeiliTTs.app"
```

### Running in dev

Run the ipynb file. It will produce things

### Serve

```bash
python -m http.server 8000
```

## Requirements

- pip install reqirements.txt
- Uses [Kokoro](https://github.com/hexgrad/kokoro?tab=readme-ov-file), so need espeak-ng package

_Note: Only works on mac rn (I assume)_
