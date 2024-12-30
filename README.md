# File Sharing System

A file management system with a Windows app and web client for quick data storage and cross-PC downloads.

## Components

- **Web Server**: Used for signup/login, manual file upload/download, and sync settings configuration
- **Windows App**: Background Python process that syncs local files with cloud changes, using signature-based authentication

## Key Features

- **Encryption**: Files are encrypted and compressed so only the original user can decode
- **Storage**: Supports most popular file types with automatic compression for better performance

## Technical Notes

### Building the Windows App

To build the executable, run:

```bash
pyinstaller --onefile \
    --hidden-import httpx \
    --hidden-import win32event \
    --hidden-import keyring.backends.Windows \
    --hidden-import watchdog \
    --hidden-import watchdog.events \
    --hidden-import watchdog.observers \
    --hidden-import tkinter \
    --hidden-import socket \
    --hidden-import pyuac \
    --hidden-import tendo \
    --hidden-import psutil \
    --hidden-import time \
    --hidden-import subprocess \
    --name "SyncApp" \
    --icon=app.ico \
    --noconsole \
    SyncApp.py
```
