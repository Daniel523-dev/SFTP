# Secure File Server

A high-performance, fully encrypted file transfer server built on top of the custom `network` secure communications module. This server provides a sandboxed virtual file system, chunk-based file transfers, and a robust JSON-based command protocol, all while inheriting the End-to-End Encryption (E2EE) guarantees of the underlying network layer.

## Core Features

*   **Sandboxed File System:** Client operations are strictly confined to a designated shared directory (defaults to `~/Shared`). The `safe_path` implementation securely resolves paths and prevents directory traversal (e.g., `../`) attacks.
*   **Chunked Transfers:** Large files are transferred using a 12MB (`CHUNK_SIZE`) limit per request. This allows for asynchronous, resumable downloads and uploads without exhausting system memory.
*   **Custom Wire Protocol:** Multiplexes JSON metadata and raw binary payloads into a single packet, allowing file commands and file data to be routed seamlessly over the encrypted connection.
*   **Comprehensive File API:** Full support for listing directories, querying file info, making directories, moving, copying, and deleting files.

## Protocol Structure

All requests and responses are framed using a custom binary packet structure handled by the `make_packet` function:
1.  **Header Length (4 Bytes):** A big-endian integer representing the size of the JSON metadata.
2.  **Metadata (Variable length):** A UTF-8 encoded JSON object containing the command (`cmd`), target path (`path`), and other required arguments.
3.  **Payload (Variable length):** Raw binary data (used primarily for file chunks during uploads/downloads).

### Supported Commands

Clients can interact with the server by sending packets with the following `cmd` values in the JSON metadata:
*   `list`: Returns the contents of a directory (name, size, and whether it's a folder).
*   `info`: Returns file metadata (size, total chunks required for download).
*   `download_chunk`: Requests a specific byte offset/chunk of a file.
*   `upload_chunk`: Writes a raw binary payload to a specific file offset.
*   `move` / `copy`: Relocates or duplicates files/directories on the server.
*   `delete`: Removes a file or directory tree.
*   `mkdir`: Creates a new directory.

## Usage

### Running the Server

You can run the server directly from the command line. It will prompt you for the necessary passwords to secure the server's long-term keys and authorize new clients.

```bash
python file_server.py
```

*Expected Output:*
```
Server password: 
Auth key password: 
[*] File Server active on tcp://127.0.0.1:9000 | Serving: /home/user/Shared
```

### Programmatic Setup

You can also import and initialize the server within your own Python scripts:

```python
import time
from file_server import FileServer

# Initialize the file server
server = FileServer(
    host="127.0.0.1",
    port=9000,
    password="SuperStrongPassword123!", 
    auth_key_password="AdminPassword456!",
    key_dir="./keys",
    salt_file="./server_salt.bin"
)

try:
    # Keep the main thread alive while the background TCP threads handle clients
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[*] Shutting down...")
    server.server.close()
```

## Security & Architecture Notes

*   **Memory Management:** By utilizing a 12MB `CHUNK_SIZE`, the server safely handles multi-gigabyte files by streaming them from disk to the network socket in segments. It never loads an entire file into RAM at once.
*   **File Integrity:** Because the server operates on top of the `network.py` AES-GCM encryption layer, all file chunks are automatically authenticated. Any tampering with the file data in transit will cause the network layer to drop the connection.

---
