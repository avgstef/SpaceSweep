# spacesweep
A sleek Windows storage utility. Scan for large files, review temporary files, and manage disk space with ease.


# SpaceSweep

**A cleaner view of your storage.**

SpaceSweep is a lightweight Windows desktop utility designed to help you understand and manage disk space through a modern, black-and-orange interface.

Explore large files, review temporary files, and get a clearer picture of your available storage — all from one desktop application.

## ✨ Features

- **Storage Dashboard** — View drive capacity, used space, and available space.
- **Large File Scanner** — Find large files and sort results by size.
- **Temporary File Review** — Scan temporary folders and review discovered files before deletion.
- **Modern Interface** — Dark surfaces, vibrant orange accents, and a custom application icon.
- **Scan Progress** — Track file-scanning progress with a percentage indicator.
- **Lightweight Desktop App** — Built with Python and Tkinter.
- **Standalone Executable** — Build a Windows `.exe` using PyInstaller.

## 🖥️ Interface

SpaceSweep features a premium black-and-orange visual identity, with a dark dashboard, orange highlights, and a custom icon designed specifically for the application.

## 📦 Installation

### Option 1 — Download the executable

1. Open the repository's **Releases** page.
2. Download the latest `SpaceSweep.exe` release, if available.
3. Run the executable on Windows.

> Releases must be published by the repository owner. If no release is available, use the source installation below.

### Option 2 — Run from source

**Requirements:** Windows and Python 3.10 or newer.

1. Clone the repository:

   ```bash
   git clone https://github.com/YOUR-USERNAME/SpaceSweep.git
   ```

2. Open the project folder:

   ```bash
   cd SpaceSweep
   ```

3. Launch the application:

   ```bash
   py spacesweep.py
   ```

## 🛠️ Build the executable

The project includes a Windows build script.

1. Make sure Python is installed and available through the `py` command.
2. Run `build.bat`.
3. Wait for PyInstaller to finish.
4. Find the generated executable in:

   ```text
   dist/SpaceSweep.exe
   ```

The build script uses the included SpaceSweep icon.

## 🔒 Safe file management

SpaceSweep is intended to help users inspect storage and review files before taking action.

- Review file paths before deleting anything.
- Avoid removing files you do not recognize.
- Close applications that may be using temporary files before cleaning them.
- Keep backups of important data.

**Important:** Deleting files can be permanent. Always verify the selected files before confirming deletion.

## 🧰 Built With

- [Python](https://www.python.org/) — Application logic
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — Desktop interface
- [PyInstaller](https://pyinstaller.org/) — Windows executable packaging

## 🗺️ Roadmap

Potential improvements for future releases:

- Additional interface polish and animations
- Further scanning performance improvements
- More detailed storage insights
- Expanded testing across Windows systems

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

If you find an issue, open a GitHub Issue with a description of the problem and steps to reproduce it.

## 📄 License

See the [`LICENSE`](LICENSE) file for the project's license terms.

---

**SpaceSweep** — Understand your storage. Keep it under control.
