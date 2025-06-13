** Still in progress..**

## MeiLiTTs App.

A lightweight (250mb :laughing:) open source TTS reader!

Upload your PDFs, watch them process locally, then follow along with them!

_only works on mac - potentially only on m3 - haven't checked anything else :p_

Main view:
![minimalistic menu showing ability to process PDFs, open existing ones](readme_assets/main-view.png)

Reader View:
![simple paragraph chunked view w/ a play button & slider](readme_assets/reader-view.png)

### Instructions

1. Download the zip. Unzip it
2. Open the folder. Double click launch.command
3. This will open a terminal window. Wait a bit
4. During the first time using this app or after the folder is moved, the environment will be rebuilt. This will take a couple of minutes
5. Enjoy!
6. Keep the terminal window open. Here you can see progress

### Information!

1. bin/ has espeak-ng stuff in it. This should just work.

2. Run `./rebuild_python.sh` to rebuild/create the python lib in MeiLiTTs w/ the python3 from your computer. Note that you need pyenv for this to work. you may have to rewrite this script- I put ~30s of asking ChatGPT into it.

3. Run `./make_release.sh` to make a release. It will clean up the python/ folder, then zip up the meili_tts_simple folder (you may need to run chmod +x first). This will fail if you don't have python3.12. Feel free to rewrite this using a LLM. This is what I did.

4. Uses [Kokoro](https://github.com/hexgrad/kokoro?tab=readme-ov-file), this is why need espeak-ng package

### TODO:

1. Get rid of old version
2. Get rid of external requirements.txt? and venv? Only really need this inside? or maybe keep it for dev
