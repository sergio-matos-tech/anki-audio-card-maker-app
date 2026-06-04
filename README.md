# Anki Audio Card Maker

<img width="703" height="570" alt="image" src="https://github.com/user-attachments/assets/aca91911-11e8-4ebf-a589-aef5de9a1cbd" />


Beta Windows app for turning bilingual lesson files and numbered MP3 files into Anki cards with audio.

This is an early beta. Right now it is focused on Windows users and lessons with English sentences, Portuguese translations, and matching numbered audio files.

## What It Does

- Reads one `.pdf` or `.txt` lesson file
- Finds English and Portuguese sentence pairs
- Matches each card to the correct numbered `.mp3` file
- Creates a tab-separated `.txt` file for Anki
- Copies the used MP3 files into your Anki media folder
- Highlights some recognized phrasal verbs

## Lesson Folder

Put the lesson document and audio files in the same folder.

Example:

```text
Lesson Folder/
  DRINK UP - Full Lesson.pdf
  1 - track.mp3
  2 - track.mp3
  3 - track.mp3
```

The audio files must start at `1` and follow the same order as the sentences in the lesson.

## Download

For normal use on Windows, download the beta executable from:

```text
dist/AnkiAudioCardMaker.exe
```

Open the app, choose your lesson folder, create the import file, then import that `.txt` file into Anki.

<img width="703" height="567" alt="image" src="https://github.com/user-attachments/assets/adc4fbd8-dac6-4482-902f-04896ad74f99" />


See [GUIDE.md](GUIDE.md) for the simple user guide.

## Import Into Anki

After the app creates the import file:

1. Open Anki.
2. Click `Import File`.
3. Select the generated `.txt` file.
4. Use `Tab` as the field separator.
5. Map field 1 to the front and field 2 to the back.
6. Import the notes.

The audio should play because the app copies the selected MP3 files into Anki's media folder.

## Run From Source

If you want to run the Python version on Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.ui
```

## Build The Executable

The project uses PyInstaller and keeps the `.spec` file in the repo:

```powershell
pip install pyinstaller
pyinstaller AnkiStreamAligner.spec
```

The executable is created in `dist/`. The `build/` folder is only temporary PyInstaller output and is ignored by Git.
