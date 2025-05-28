## TODO:

1. Get rid of old version
2. Get rid of external requirements.txt? and venv? Only really need this inside? or maybe keep it for dev idk.
3. Streamline the python/ creation & some stuff in that vein.

### New minimal version!

bin/ has espeak-ng stuff in it

python/ folder created with cp -R <pyenv which python3> python/

Run `./make_release.sh` to make a release. It will clean up the python/ folder, and then zip up the meili_tts_simple folder (you may need to run chmod +x first)

## Requirements

- pip install reqirements.txt
- Uses [Kokoro](https://github.com/hexgrad/kokoro?tab=readme-ov-file), so need espeak-ng package

_Note: Only works on mac rn (I assume)_
