import errno
import logging
import os
import stat
if os.name != "posix":raise RuntimeError("This program requires a POSIX operating system.")
import fuse
from fuse import FUSE, Operations


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("FUSE")
CHUNK_SIZE = 16 * 1024 * 1024


# ==========================================
# SHARED STORAGE WITH CALLBACKS
# ==========================================

class SharedStorage:
    """In-memory storage manager used by FUSE."""

    def __init__(self):
        self._files = {}
        self._dirs = {""}
        self.callbacks = {
            "read": None,
            "write": None,
            "delete": None,
            "mkdir": None,
        }

    def on(self, event, callback):
        self.callbacks[event] = callback

    def _clean(self, key):
        return str(key).replace("\\", "/").strip("/")

    def exists(self, key):
        return self._clean(key) in self._files

    def is_dir(self, key):
        key = self._clean(key)

        if not key:
            return True

        return (
            key in self._dirs
            or any(
                k.startswith(key + "/")
                for k in self._files
            )
        )

    def get_size(self, key):
        key = self._clean(key)
        return len(self._files.get(key, b""))

    def read(self, key):
        key = self._clean(key)

        if self.callbacks["read"]:
            self.callbacks["read"](key)

        return self._files.get(key, b"")

    def _get_data(self, key):
        return self._files.get(
            self._clean(key),
            b"",
        )

    def write(self, key, data):
        key = self._clean(key)

        if self.callbacks["write"]:
            self.callbacks["write"](key, data)

        self._files[key] = data

        parts = key.split("/")

        for i in range(1, len(parts)):
            self._dirs.add(
                "/".join(parts[:i])
            )

    def write_chunk(self, key, offset, chunk_bytes):
        key = self._clean(key)
        existing = self._files.get(key, b"")

        new_data = (
            existing[:offset]
            + chunk_bytes
            + existing[offset + len(chunk_bytes):]
        )

        self.write(key, new_data)
        return True

    def read_chunk(self, key, offset, size):
        data = self.read(key)

        return data[
            offset:offset + size
        ]

    def delete(self, key):
        key = self._clean(key)

        if self.callbacks["delete"]:
            self.callbacks["delete"](key)

        if key in self._files:
            del self._files[key]

    def mkdir(self, key):
        key = self._clean(key)

        if self.callbacks["mkdir"]:
            self.callbacks["mkdir"](key)

        self._dirs.add(key)

    def list_keys(self):
        return list(
            set(self._files.keys()).union(
                self._dirs
            )
        )


# ==========================================
# FUSE
# ==========================================

class StorageFUSE(Operations):
    def __init__(self, storage):
        self.storage = storage
        self.fd_count = 0

    def getattr(self, path, fh=None):
        path = path.lstrip("/")

        if not path or self.storage.is_dir(path):
            return {
                "st_mode": stat.S_IFDIR | 0o755,
                "st_nlink": 2,
            }

        if self.storage.exists(path):
            return {
                "st_mode": stat.S_IFREG | 0o644,
                "st_nlink": 1,
                "st_size": self.storage.get_size(path),
            }

        raise fuse.FuseOSError(
            errno.ENOENT
        )

    def readdir(self, path, fh):
        path = path.lstrip("/")
        prefix = f"{path}/" if path else ""
        dirents = [".", ".."]

        for key in self.storage.list_keys():
            if key.startswith(prefix):
                rel = key[len(prefix):].split("/")[0]

                if rel and rel not in dirents:
                    dirents.append(rel)

        return dirents

    def read(self, path, size, offset, fh):
        return self.storage.read_chunk(
            path.lstrip("/"),
            offset,
            size,
        )

    def write(self, path, data, offset, fh):
        self.storage.write_chunk(
            path.lstrip("/"),
            offset,
            data,
        )

        return len(data)

    def unlink(self, path):
        self.storage.delete(
            path.lstrip("/")
        )

    def create(self, path, mode, fi=None):
        self.storage.write(
            path.lstrip("/"),
            b"",
        )

        self.fd_count += 1
        return self.fd_count

    def mkdir(self, path, mode):
        self.storage.mkdir(
            path.lstrip("/")
        )


# ==========================================
# EXAMPLE
# ==========================================

def main():
    storage = SharedStorage()

    mountpoint = "./mount"

    os.makedirs(
        mountpoint,
        exist_ok=True,
    )

    FUSE(
        StorageFUSE(storage),
        mountpoint,
        foreground=True,
        nothreads=False,
    )


if __name__ == "__main__":
    main()