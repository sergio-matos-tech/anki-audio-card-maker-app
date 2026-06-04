# Anki Media Stream Aligner (AnkiStreamAligner)

Automatically converts bilingual lesson material and matching audio files into Anki-ready flashcards with perfectly synchronized audio.

---

## Overview

When studying a foreign language, high-quality flashcards with synchronized audio can significantly improve retention and listening comprehension.

Unfortunately, creating those cards manually is often tedious:

* PDFs contain headers, footers, advertisements, and URLs.
* Lesson content is frequently mixed with formatting noise.
* Audio files are stored separately.
* Small parsing mistakes can desynchronize the entire deck.

Anki Media Stream Aligner automates this workflow by extracting bilingual sentence pairs, preserving audio alignment, and generating files ready for direct import into Anki.

---

## Features

* Extracts bilingual sentence pairs from PDF and TXT documents
* Removes URLs, headers, and document noise
* Preserves sentence-to-audio synchronization
* Automatically copies audio files to Anki's media directory
* Generates Anki-compatible tab-separated files
* Supports Windows and Linux
* Thread-safe background processing
* GUI-based workflow
* Automated integration testing

---

## Why This Exists

Traditional parsing scripts often process lesson content line by line.

This creates a common failure mode:

### Example

Document:

```text
She ran up a massive bill. Ela acumulou uma conta enorme.
```

A naive parser may incorrectly split this into multiple cards.

Once that happens:

| Card | Audio   |
| ---- | ------- |
| 1    | Audio 1 |
| 2    | Audio 2 |
| 3    | Audio 4 |
| 4    | Audio 5 |

The entire deck becomes desynchronized.

Anki Media Stream Aligner guarantees:

```text
Sentence N → Audio N
```

throughout the entire import pipeline.

---

## Example

### Input Document

```text
She drank up all the milk.
Ela bebeu todo o leite.

The children drank up the juice.
As crianças beberam todo o suco.
```

### Input Audio Files

```text
1 - track.mp3
2 - track.mp3
```

### Generated Output

```text
She drank up all the milk. [sound:1.mp3]	Ela bebeu todo o leite.
The children drank up the juice. [sound:2.mp3]	As crianças beberam todo o suco.
```

The output is immediately compatible with Anki's import system.

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/AnkiMediaStreamAligner.git
cd AnkiMediaStreamAligner
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate the Environment

#### Windows

```powershell
.venv\Scripts\activate
```

#### Linux

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Expected Input Structure

Place your lesson document and matching audio files inside the same folder.

```text
Lesson Folder/
│
├── DRINK UP - Full Lesson.pdf
├── 1 - track.mp3
├── 2 - track.mp3
├── 3 - track.mp3
└── ...
```

### Requirements

* One PDF or TXT file containing bilingual lesson content
* Sequentially numbered MP3 files
* Audio numbering must begin at 1

---

## Usage

### Launch the Application

```bash
python -m src.ui
```

### Configure the Application

#### Anki Profile Name

Enter your Anki profile name.

Default:

```text
User 1
```

The application will automatically locate the corresponding Anki media folder.

#### Select Source Folder

Choose the folder containing:

* Lesson PDF/TXT
* MP3 files

---

## Generate and Synchronize Assets

Click:

```text
⚡ GENERATE & SYNC ASSETS
```

The application will:

1. Parse the lesson document
2. Extract bilingual sentence pairs
3. Preserve sentence-to-audio alignment
4. Generate an Anki-compatible TXT file
5. Automatically copy audio files into Anki's media directory
6. Open a save dialog for the generated file

Example output filename:

```text
DRINK UP.txt
```

---

## Importing into Anki

Once the file has been generated:

1. Open Anki
2. Click **Import File**
3. Select the generated TXT file

### Import Settings

| Setting             | Value                              |
| ------------------- | ---------------------------------- |
| Note Type           | Basic (Básico) or custom note type |
| Target Deck         | Any deck of your choice            |
| Fields separated by | Tab (Tabulação)                    |

### Field Mapping

| Input Field | Anki Field |
| ----------- | ---------- |
| Field 1     | Front      |
| Field 2     | Back       |

### Front Side

Contains:

* English sentence
* Automatic keyword highlighting
* Audio reference

Example:

```text
She drank up all the milk. [sound:1.mp3]
```

### Back Side

Contains:

* Portuguese translation
* Noise-free content
* No URLs
* No document artifacts

Click **Import** to finish.

---

## Technical Architecture

### Design Principles

The application follows a decoupled architecture designed for maintainability and testability.

### Core Components

* Parser Engine
* Sentence Alignment Engine
* Audio Synchronizer
* Anki Media Resolver
* GUI Layer

### Thread-Safe Processing

Heavy operations execute on background worker threads.

Communication with the user interface occurs through a thread-safe message queue, ensuring:

* Responsive UI
* Safe concurrency
* Predictable execution flow

### Testing

The project includes automated end-to-end tests using:

* Temporary file systems
* Mocked components
* Integration test suites

This helps prevent regressions and ensures stable behavior across releases.

---

## Roadmap

* [ ] macOS support
* [ ] Direct AnkiConnect integration
* [ ] Batch lesson processing
* [ ] Deck creation automation
* [ ] Drag-and-drop folder support
* [ ] Processing statistics dashboard
* [ ] Automatic deck import

---

## Contributing

Contributions, bug reports, and feature requests are welcome.

Feel free to open an issue or submit a pull request.

---

## License

MIT License
