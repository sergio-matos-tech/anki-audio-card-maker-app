# Anki Stream Aligner

Anki Stream Aligner turns bilingual lesson text and matching MP3 files into an Anki import file with synchronized audio.

The app is built for lessons that have:

- One `.pdf` or `.txt` file with English sentences and Portuguese translations
- Numbered `.mp3` files for the same sentences
- Audio files that start at `1` and follow the lesson order

Example:

```text
Lesson Folder/
  DRINK UP - Full Lesson.pdf
  1 - track.mp3
  2 - track.mp3
  3 - track.mp3
```

## What It Does

- Finds bilingual sentence pairs in the lesson document
- Matches each card to the correct numbered audio file
- Creates a tab-separated `.txt` file that Anki can import
- Copies the used audio files into your Anki media folder
- Highlights the target phrasal verb when the parser recognizes it

The generated file looks like this:

```text
She drank up all the milk. [sound:1 - track.mp3]	Ela bebeu todo o leite.
The children drank up the juice. [sound:2 - track.mp3]	As criancas beberam todo o suco.
```

## Download

For normal use, download the Windows executable from:

```text
dist/AnkiStreamAligner.exe
```

Run the executable, choose your lesson folder, and import the generated `.txt` file into Anki.

See [GUIDE.md](GUIDE.md) for the full user guide.

## Run From Source

If you want to run the Python version:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt customtkinter
python -m src.ui
```

## Build The Executable

The project uses PyInstaller and keeps the `.spec` file in the repo:

```powershell
pip install pyinstaller
pyinstaller AnkiStreamAligner.spec
```

`dist/` contains the user-facing executable. `build/` is only a temporary PyInstaller folder and is ignored by Git.

## Import Into Anki

After the app creates the import file:

1. Open Anki.
2. Click `Import File`.
3. Select the generated `.txt` file.
4. Use `Tab` as the field separator.
5. Map field 1 to the front and field 2 to the back.
6. Import the notes.

The audio should play because the app copies the selected MP3 files into Anki's media folder.
