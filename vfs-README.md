# POSIX Virtual File System (VFS)

A Python-based FUSE (Filesystem in Userspace) bridge designed for POSIX-compliant operating systems (Linux, macOS). This module translates standard OS-level file operations into Python method calls, allowing you to mount custom storage backends`like an in-memory dictionary or a remote encrypted server`as a standard local directory.

## Core Components

*   **`SharedStorage`:** A default, in-memory storage manager. It simulates a file system using Python dictionaries and sets. It also provides a robust callback system (`on()`) to monitor read, write, delete, and mkdir events in real-time.
*   **`StorageFUSE`:** The core FUSE operations handler. It inherits from `fuse.Operations` and intercepts OS calls (like `getattr`, `readdir`, `read`, `write`, `unlink`), routing them to the underlying storage object.

## How It Fits In

In the context of the Secure File Server/Client ecosystem, this script serves as the Linux/macOS mounting backend. While the default `SharedStorage` runs purely in RAM, the `StorageFUSE` class is designed to accept *any* storage object that implements the same methods. 

For example, the `client.py` script injects its `RemoteStorage` network class into `StorageFUSE`, mapping network requests directly to local file explorer actions.

## Requirements

*   **OS:** A POSIX-compliant operating system (Linux, macOS). Windows is explicitly blocked and will raise a `RuntimeError`.
*   **System Packages:** `libfuse` must be installed on your OS (e.g., `sudo apt install libfuse2` on Ubuntu).
*   **Python Packages:** The `fusepy` library is required to interface with FUSE.

## Usage

### 1. Running the In-Memory Example

If you run the script directly, it will spin up a local, purely in-memory file system and mount it to a folder named `./mount` in your current directory.

```bash
python vfs.py
```

Once running, you can open a second terminal and interact with the `./mount` directory as if it were a normal folder. Any files you create or copy there will be stored in your computer's RAM. When you stop the script (Ctrl+C), the files vanish.

### 2. Using it as a Library (Injecting Custom Storage)

You can write your own storage class and pass it to `StorageFUSE` to mount databases, cloud buckets, or remote servers.

```python
import os
from fuse import FUSE
from vfs import StorageFUSE

# 1. Define your custom storage class with the required methods
class MyCustomStorage:
    def exists(self, key): ...
    def is_dir(self, key): ...
    def get_size(self, key): ...
    def read_chunk(self, key, offset, size): ...
    def write_chunk(self, key, offset, data): ...
    def delete(self, key): ...
    def mkdir(self, key): ...
    def list_keys(self): ...

# 2. Mount it
mountpoint = "/mnt/my_custom_drive"
os.makedirs(mountpoint, exist_ok=True)

print(f"Mounting custom drive at {mountpoint}...")
FUSE(
    StorageFUSE(MyCustomStorage()), 
    mountpoint, 
    foreground=True, 
    nothreads=False
)
```

## Architecture Notes

*   **Chunking:** The module uses a `CHUNK_SIZE` of 16MB. When standard applications (like video players or text editors) request to read a file, `StorageFUSE` translates these into `read_chunk` and `write_chunk` requests, ensuring large files don't overload memory.
*   **Path Sanitization:** FUSE passes paths with a leading slash (e.g., `/folder/file.txt`). The storage manager automatically strips these via `_clean()` to ensure consistent internal key mapping.
