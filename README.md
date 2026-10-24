# SpaceSweep

**A polished, local-first Windows storage utility.**

SpaceSweep helps you understand disk usage, locate large files, and review temporary files before cleanup.

## Features

- Premium black-and-orange interface with custom app icon, soft startup fade, orange accent glow, and smooth Segoe UI typography
- Drive capacity, used space, and free-space overview
- Recursive large-file scanner, sorted by size, with a live percentage progress indicator
- User temporary-folder scanner with live percentage progress
- Manual file selection and confirmation before permanent deletion
- Safe handling of inaccessible files and symbolic links
- Local-first: no account or cloud upload functionality

## Screens / sections

- **Overview** — drive capacity cards and quick actions
- **Large files** — scan a selected folder and inspect the largest files
- **Cleanup** — review temporary files and choose what to delete
- **Duplicates** — roadmap screen for the next build
- **Settings** — safety boundaries and build information

## Run from source

1. Install Python 3.10+ from https://www.python.org/downloads/windows/
2. Enable **Add Python to PATH** during installation.
3. Run `run.bat` or execute `py spacesweep.py`.

## Build a standalone EXE

Run `build.bat`. It installs PyInstaller and builds `dist\SpaceSweep.exe`.

The build requires internet access to install PyInstaller. The executable does not require Python to be installed separately.

## Safety

- The large-file scanner reads file metadata and does not modify scanned files.
- Cleanup only scans the current user's temporary directory.
- Deletion requires selecting files and confirming the action.
- Deletion is permanent and does not use the Recycle Bin.
- Files in use or without sufficient permissions may be skipped.
- Always review paths before deleting files.

## Known limitations

- Duplicate detection is a roadmap placeholder in this version.
- Scans may take time on large folders. A cancel button is not implemented yet.
- The app is not digitally signed; Windows may display a reputation warning for a self-built executable.

## License

MIT. See `LICENSE`.


## Visual identity

The app uses a custom black-and-orange icon (`spacesweep.ico` / `spacesweep.png`), a restrained orange accent glow, startup fade-in, and determinate scan progress. Progress is based on a file-counting pass followed by the metadata scan, so scans perform two directory traversals for an honest percentage.
