# Bitmem
# BitMem

**BitMem** is an open-source RAM imaging tool developed as part of a cybersecurity graduation project. It creates a bitwise copy of a system’s RAM and includes optional analysis features using Volatility and image mounting.

## Versions

BitMem is available in two formats:

- **Python script**: `bitmem.py`
- **Windows executable**: `bitmem.exe`

## Requirements

- Administrator privileges are required to run either version.
- For the Python version:
    - Python 3.x
    - WinPmem for memory acquisition
    - Volatility (2 or 3) for memory analysis

## Usage

### Python Version

To run the Python script, open an **Administrator Command Prompt** and execute:

```bash
python bitmem.py
```

### Executable Version

To run the executable, right-click `bitmem.exe` and choose **Run as Administrator**.

## Features

- Bitwise RAM acquisition using WinPmem
- Generation of hash values (MD5 and SHA1, …) for integrity verification
- Optional memory analysis using Volatility
- Option to mount the acquired memory image for inspection
- Clear console output and logging for each step
