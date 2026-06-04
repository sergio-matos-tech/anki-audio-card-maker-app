# 📥 Automated Anki Import Guide

This guide provides a step-by-step walkthrough to import your parsed flashcard text file (e.g., `DRINK UP.txt`) and matching audio assets into Anki on both Windows 11 and Linux.

---

## 🛠️ Prerequisites

Before starting, ensure you have run the Python script and have:

* The dynamically generated text file in your project root (e.g., `DRINK UP.txt` or `WORK UP.txt`)
* All corresponding sequential `.mp3` files in your `./inputs` directory

---

## 🚀 Step-by-Step Instructions

### Step 1: Move Audio Files to Anki's Media Directory

For Anki to play audio natively using the `[sound:...]` tags, your `.mp3` files must reside in Anki's global media directory rather than your local development folder.

Copy all numbered `.mp3` files from your project's `inputs` directory and paste them into your system's Anki media folder as specified below.

---

### 🪟 Windows 11

1. Press **Win + R** on your keyboard to open the **Run** dialog box.
2. Type the following path and press **Enter**:

```text
%APPDATA%\Anki2
```

3. Open your profile folder (usually named **User 1** or your custom username).
4. Open the **collection.media** folder.
5. Paste your audio files into this directory.

---

### 🐧 Linux

Depending on how you installed Anki, copy the files to the appropriate path.

#### Standard / Native Installation

```text
~/.local/share/Anki2/User 1/collection.media/
```

#### Flatpak Installation

```text
~/.var/app/net.ankiweb.Anki/.local/share/Anki2/User 1/collection.media/
```

> Replace `User 1` with your actual profile name if you customized it.

> **Note:** Do not copy the full lesson audio file (the long, unnumbered `.mp3` file). The pipeline is configured to sync only the indexed audio files.

---

### Step 2: Import the Text File

With your audio assets safely placed in Anki's media directory, you can now import your structured bilingual text.

1. Open **Anki**.
2. Click the **Import File** button at the bottom of the main window.
3. Navigate to your project directory (e.g., `AnkiForge` or your custom folder).
4. Select the generated phrasal verb text file (e.g., `DRINK UP.txt`).

---

### Step 3: Configure Mapping and Import

An import options window will open. Apply the following settings to guarantee perfect stream alignment.

#### Import Settings

| Setting             | Value                                             |
| ------------------- | ------------------------------------------------- |
| Type                | Basic (Básico) or your custom language note type  |
| Deck                | Your target deck (e.g., `English::Phrasal Verbs`) |
| Fields separated by | Tab (Tabulação)                                   |

#### Field Mapping

Verify that Anki maps the fields as follows:

| Input Field | Anki Field | Description                                                                       |
| ----------- | ---------- | --------------------------------------------------------------------------------- |
| Field 1     | Front      | English sentence with automatic HTML `<u>` underscoring and the `[sound:...]` tag |
| Field 2     | Back       | Clean Portuguese translation                                                      |

5. Click **Import** in the top-right corner.

---

## 🎯 Expected Result

Anki will immediately process the file and display a success log indicating that **15 notes** have been added.

When studying your deck:

### Front Side

* Displays the English sentence
* Automatically underscores the phrasal verb
* Plays the synchronized audio clip immediately

### Back Side

* Reveals the clean Portuguese translation
* Contains no URLs, PDF artifacts, or layout noise
