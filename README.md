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
    --hidden-import winerror \
    --hidden-import win32api \
    --hidden-import win32event \
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

## Project Idea

A file management system with a Windows app and a web client that can store data quickly and allow quick download to any PC.

- **Web Server**: Used for signup/login, allows manual file upload to the cloud and download, and configure sync settings.
- **App**: Python instance that updates local files when changed in the cloud, has a signature so you don't have to enter a password. (feat' gui elements for var setting.)

### Key Features

- **Encryption**: Ensure the files are encrypted and compressed when uploaded in a way that only the original user can decode.
- **Storage**: Support most popular files and zip them automatically for better performance.

### Challenges

just the sheer amount of different things i have to do. this is a big project. ill need to do encryptions, python js html windows and so many more things alone. 
i dont think there's a specific part where ill have much more trouble but the whole thing will take time and is complicated for my level.

### Development Plan

1. Start with a proof of concept to make sure the hardest parts are possible. It will be minimalistic.
2. Create the API - the web server.
3. Lastly, develop the app.

### New Technologies to Learn

- encryptions
- SQLite3
- js
- HTML
- CSS
- py => windows

### Estimated Time

I think this project, if executed to the fullest, will take over 400 hours.

### Encryption and File Sharing

דיברתי עם מוטי. הבנו דרך מעניינת לבצע הצפנה ואת השיתוף של קבצים.
בזמן העלאה ראשונה המשתמש יזין מאסטר פסוורד בגאווה אני אעשה האש לסיסמאת מאסטר והאש לאיי די מגונרט של הקובץ. אני אחבר אותם ואמעך בעזרת האש כדי להשיג סיסמה מיוחדת לאיי אי אס להצפנת הקובץ. שם הקובץ שישלח לשרת והתוכן יוצפנו עם הסיסמא המיוחדת.
בזמן שיתוף המשתמש יקבל מייל עם יו אר אל עם ה איי די הספציפי של הקובץ המשותף וסיסמא לתוכן שלו לאחר פתיחת הקישור יתבקש להזין את הסיסמא ויקבל קובץ להורדה.

### Current Focus

right now ill be focusing on the app since i dont really feel like working to the html gui and i can learn about the reconstruction 
and decryption easier with this type of applicatio
