# Secure Encrypted SFTP

Welcome to the Secure File Transfer project. This repository contains a complete, end-to-end encrypted remote file storage ecosystem. It allows you to host a secure file server and mount it on client machines (Windows and Linux) as a native local drive. Files are encrypted and decrypted on the fly in memory, ensuring that your data remains secure both in transit and at rest.

## Project Structure & Documentation

The project is broken down into several modular components. For detailed instructions on how to use, configure, or develop each piece, please refer to their respective README files:

* **Server Component** (`server-README.md`): Instructions for running and configuring the secure remote storage backend.
* **Client Component** (`client-README.md`): Guide for using the Python client API and mounting the remote server as a local drive.
* **Cryptography** (`Encryption-README.md`): Overview of the cryptographic backbone (Argon2, AES-GCM, ChaCha20, X25519/Ed25519) securing the entire ecosystem.
* **Networking** (`network-README.md`): Explanation of the custom TCP packet framing and streaming protocol used for zero-knowledge data transfer.
* **Linux Mount** (`vfs-README.md`): Details on the POSIX-compliant FUSE bridge for Unix-like systems.
* **Windows Mount** (`winfuse2-README.md`): Details on the Windows virtual drive integration, which is powered by the Windows Cloud Files API (`cfAPI`) rather than traditional FUSE.
## Optional: TPM Autofill Integration

Optional autofill functionality is provided by the separate Psudo-TPM repository, available at:
```url
https://github.com/Daniel523-dev/Psudo-TPM
```
This component is not included in this repository and must be obtained separately.

To enable autofill, download `TPM.exe` from the most recent release in the Psudo-TPM and download `TPM_client.py`. Place both `TPM.exe` and `TPM_client.py` in the current working directory on **both the server and client machines**.

The TPM integration is entirely optional and is not required for the core encrypted file storage, network communication, or drive-mounting functionality.

## License

This software is released under the **GNU General Public License v3.0 (GPL-3.0)**.

Please see the `LICENSE` file for the full text of the license, your rights, and your obligations when using or modifying this software.
