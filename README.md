# File Sharing System

A file management system with a web client for quick data storage and cross-PC downloads.

## Components

- **Web Server**: Used for signup/login, manual file upload/download, and sync settings configuration

## Key Features

- **Encryption**: Files are encrypted and compressed so only the original user can decode
- **Storage**: Supports most popular file types with automatic compression for better performance



## Project Idea

A file management system with a web client that can store files quickly and securly, and can grant easy access to them on any pc.

### Key Features

- **Encryption**: Ensure the files are encrypted and compressed when uploaded in a way that only the original user can decode.
- **Storage**: Support most popular files and zip them automatically for better performance.

### Challenges

just the sheer amount of different things i have to do. this is a big project. ill need to do encryptions, python js html windows and so many more things alone. 
i dont think there's a specific part where ill have much more trouble but the whole thing will take time and is complicated for my level.

### Development Plan

1. Write an MVP - (minimal viable product) with the ability to digest files and store them in the server.
2. create a database system and implement user login and signup.
3. write html,js,css for onboarding and getting into the main page.
4. start testing encrypting, compressing methods that work best for my usecase.
5. work on the storing system - add support for folders.
6. finishing touches.

### New Technologies to Learn

- encryptions
- SQLite3
- js
- HTML
- CSS

### Estimated Time

I think this project, if executed to the fullest, will take over 400 hours.

### Encryption and File Sharing

Shared files will be kept localy as a one time download asset. for minimal security risk the time it's on our system is minimal.
Encryption of common files is done using AES on chunked parts of each file with the key being a hash of the user's password his username some known salt, and lastly the id of the file - in a certain combination.
this way even in a case of database\file system leak no one will be able to regain the original content of the file.
