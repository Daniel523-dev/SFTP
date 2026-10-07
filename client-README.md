# Secure FUSE Client

The client-side counterpart to the Secure File Server. This client not only provides a Python API for interacting with the remote file system but also leverages FUSE (Filesystem in Userspace) to mount the remote encrypted file system as a local folder/drive on both Windows and Linux.

## Core Features

*   **Virtual Drive Mounting:** Mounts the remote server seamlessly as a local drive folder. You can drag, drop, open, and edit files using your native OS file explorer (Windows Explorer, GNOME Files, etc.).
*   **Cross-Platform Support:** Automatically detects the host OS. Uses `winfuse2` on Windows and standard FUSE (via `vfs`) on Linux.
*   **Zero-Knowledge Streaming:** Files are streamed in 12MB chunks (`CHUNK_SIZE`) and encrypted/decrypted on the fly. Huge files never touch your local disk unencrypted unless explicitly saved.
*   **Event Callbacks:** Provides a robust hook system (`storage.on(...)`) to track read, write, delete, and mkdir operations in real-time.
*   **Remote File-Like Objects:** Includes a `RemoteReader` class that behaves like a standard Python file object, supporting `read()`, `seek()`, and `tell()` over the encrypted network.

## Requirements

*   **Windows:** Requires `winfuse2` and its underlying dependencies (like WinFsp).
*   **Linux:** Requires the `vfs` module (a FUSE wrapper) and the OS-level `libfuse` / `fuse` package.
*   The underlying `network.py` module must be present in the same directory.

## Usage

### 1. Mounting the Remote Drive (CLI)

Running the script directly will attempt to connect to the server and mount the remote file system to your local machine. 

```bash
python client.py ./path/to/auth_key
```

*Expected Output:*
```text
Client password: 
Auth Key Password: 
[*] Starting WinFUSE at C:\Users\murphy2607\mount...
[READ] /example.txt
[WRITE] /new_file.png (2048 bytes)
```
*(Note: The mount point defaults to `C:\Users\murphy2607\mount` on Windows and `/mnt/remote-storage` on Linux. Make sure these directories exist or modify the script to fit your system).*

### 2. Programmatic API Usage

If you don't want to mount the drive via FUSE, you can use the `RemoteStorage` class as a powerful API to interact with the server directly from your own Python code.

```python
from client import RemoteStorage, auth_key_password_callback

# Initialize the storage connection
storage = RemoteStorage(
    host="127.0.0.1",
    port=9000,
    key_path="./auth_key",
    password="MyStrongPassword123!",
    auth_key_password_callback=auth_key_password_callback
)

# Upload a local file
storage.write_file_from_local("./local_document.pdf", "/remote_document.pdf")

# Read a remote file directly into memory
data = storage.read("/remote_document.pdf")

# Use the file-like RemoteReader interface
with storage.open_read("/remote_document.pdf") as f:
    f.seek(1024) # Skip the first KB
    chunk = f.read(512) # Read the next 512 bytes

# List directory contents
print("Files:", storage.listdir("/"))
```

## Under the Hood

*   **Packet Parsing:** Just like the server, the client uses `make_packet` and `parse_packet` to assemble and disassemble the custom 4-byte length header, JSON metadata, and binary payload format.
*   **Thread Safety:** The `RemoteStorage` class utilizes a `threading.Lock()` when making network requests (`_request`) to ensure that concurrent file I/O operations (like background file explorer thumbnails loading while you are transferring a file) do not scramble the TCP socket buffer.
