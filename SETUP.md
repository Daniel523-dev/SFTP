# SFTP Program Setup Guide

This guide explains how to set up the SFTP server and client, configure password autofill using Psudo-TPM (optional), and authorize new clients to connect to the server.

## Table of Contents

- [1. Server Setup](#1-server-setup)
- [2. Client Setup](#2-client-setup)
- [3. Granting Client Access](#3-granting-client-access)
- [4. Storage Locations](#4-storage-locations)
- [5. Security Notes](#5-security-notes)
- [Client Capacity and Scalability](#client-capacity-and-scalability)
---

## 1. Server Setup

The server can run on either Windows or Linux.

### Step 0: Install Python and Dependencies

Install a compatible Python version on the server. Ensure Python and pip are available from your terminal.

Install the following Python packages:

- cryptography
- argon2-cffi
- numpy
- pyzmq
- blake3
- zxcvbn

You can install these dependencies with pip:

    python -m pip install cryptography argon2-cffi numpy pyzmq blake3 zxcvbn

On Linux, you may need to use python3 instead of python, depending on your distribution.

### Step 1: Download the Server Files

Download the following Python source files and place them together in the same directory:

- Encryption.py
- network.py
- server.py
- util.py

If these files are hosted in a Git repository, you can obtain them by cloning the repository or downloading its source files. If you download an archive, extract its contents before continuing.

### Step 2: Configure Optional Password Autofill

This step is optional. Skip it if you do not want to use password autofill.

To enable password autofill, download the following files:

- TPM.exe — the latest release from the Psudo-TPM repository.
- TPM_client.py — the corresponding client-side Python module.

Repository: https://github.com/Daniel523-dev/Psudo-TPM

Place both files in the same directory as the server files downloaded in Step 1.

**Platform limitation:** Psudo-TPM relies on Windows Data Protection API (DPAPI), so this feature is available only on Windows.

### Step 2.5: Install Additional Psudo-TPM Dependencies

This step is required only if you enabled Psudo-TPM in Step 2.

Install the following Python packages:

- zstandard
- pywin32

Run:
```shell
    python -m pip install zstandard pywin32
```
These dependencies are intended for the Windows Psudo-TPM integration and are not required when password autofill is disabled.

### Step 3: Start the Server

Launch the server using the appropriate command for your environment.

For example, if the server entry point is server.py, run:
```shell
    python server.py
```
Follow any prompts displayed during startup.

### Step 4: Configure the Master Server Password

When prompted, create a master server password.

**Choose a very strong, unique password.** This password protects the server's master key material and should not be reused for other accounts or services.

An authentication key password is not required for normal server operation. However, if a sufficiently strong master password is not provided, the server disables new-client bootstrapping.

This restriction is useful when you do not intend to authorize additional clients. Disabling bootstrapping reduces the server's exposure to denial-of-service (DoS) attacks targeting the client enrollment process.

The server setup is now complete.

---

## 2. Client Setup

The client can run on Windows or Linux. Some dependencies and source files differ by operating system.

### Step 0: Install Python and Dependencies

Install a compatible Python version and ensure pip is available.

#### Windows

Install the following packages:

- watchdog
- pyzmq
- zxcvbn
- cryptography
- argon2-cffi
- blake3

Run:
```shell
    python -m pip install watchdog pyzmq zxcvbn cryptography argon2-cffi blake3
```
#### Linux

Install the following packages:

- fusepy
- pyzmq
- zxcvbn
- cryptography
- argon2-cffi
- blake3

Run:
```shell
    python3 -m pip install fusepy pyzmq zxcvbn cryptography argon2-cffi blake3
```
The Linux client uses FUSE to expose remote storage through a filesystem mount point. Depending on your distribution, you may also need to install the appropriate system-level FUSE packages and configure the required permissions.

### Step 1: Download the Client Files

Download the following Python source files and place them together in the client directory:

- Encryption.py
- network.py
- client.py
- util.py

Additionally, download the platform-specific filesystem integration:

- **Linux:** vfs.py
- **Windows:** winfuse2.py

If the source files are hosted in a Git repository, you can clone the repository or download and extract its source archive.

### Step 2: Configure Optional Password Autofill

This step is optional.

To enable password autofill, download the following files from the Psudo-TPM repository:

- TPM.exe — the latest release.
- TPM_client.py — the client-side Python module.

Repository: https://github.com/Daniel523-dev/Psudo-TPM

Place both files in the same directory as the client files downloaded in Step 1.

**Important:** Psudo-TPM relies on Windows DPAPI and therefore works only on Windows. Do not expect this feature to work on Linux.

### Step 2.5: Install Additional Psudo-TPM Dependencies

If you enabled Psudo-TPM, install:

- zstandard
- pywin32

Run:
```shell
    python -m pip install zstandard pywin32
```
Skip this step if you are not using Psudo-TPM.

### Step 3: Request Server Access

Contact the server administrator and request authorization to connect.

Client authorization is handled out-of-band, meaning the authorization credentials are exchanged through a separate communication channel rather than through the normal SFTP connection.

The administrator must complete the server-side authorization procedure in the next section before you can bootstrap your client.

---

## 3. Granting Client Access

This section describes how the server administrator authorizes a new client.

### Server Administrator Instructions

#### Step 1: Restart the Server

Restart the server to begin the client authorization process.

#### Step 2: Configure an Authentication Key Password

During startup, enter a secure authentication key password when prompted.

The authentication key password has lower strength requirements than the master server password, but it should still be difficult to guess and kept confidential.

This password protects the temporary authorization key used during client bootstrapping.

#### Step 3: Transfer the Authentication Key to the Client

Give the client a copy of the following file:
```
    ./keys/auth_key
```
Communicate the corresponding authentication key password to the client through a separate, trusted channel.

Do not send the key and its password through an untrusted channel.

### Important: Authentication Keys Are Single-Use

The server invalidates and discards its current authentication key whenever the server restarts or a client attempts to bootstrap.

Consequently:

- Each authentication key is valid for a single bootstrapping attempt.
- A key may become invalid before it is used if the server restarts.
- A key may become invalid if another client attempts to bootstrap first.
- If a key is invalidated, the administrator must generate and distribute a new one.

**Always coordinate the key transfer and bootstrapping process with the server administrator.** Do not assume an authentication key remains valid indefinitely.

### Client Instructions

#### Step 1: Obtain the Authentication Key

Obtain the authentication key file and its password from the administrator through the agreed out-of-band communication channel.

Place the file in the client's current working directory (the directory from which the SFTP client will be launched).

The file should be named:
```
    auth_key
```
#### Step 2: Start the SFTP Client

Launch the client using the appropriate command for your environment.

For example, if client.py is the entry point, run:
```shell
    python client.py
```
On Linux, you may need to use python3 instead.

#### Step 3: Configure the Master Client Password

When prompted, create a master client password.

**Choose a very strong, unique password.** This password protects the client's master key material.

Keep this password safe. Do not reuse your server password or an unrelated account password.

#### Step 4: Enter the Authentication Key Password

When prompted, enter the authentication key password provided by the server administrator.

If the key is valid and the bootstrapping process succeeds, the client will complete its initial authorization.

**Note:** During bootstrapping, the client overwrites its local auth_key file. Make sure you have placed the correct authorization key in the client's working directory before starting the process.

---

## 4. Storage Locations

The server and client use the following default storage locations.

| Component | Operating system | Location |
|---|---|---|
| Server shared files | Windows or Linux | ~/Shared |
| Client mount point | Linux | /mnt/remote-storage |
| Client mount point | Windows | ~/mount |

The server stores its shared files under ~/Shared. The client accesses remote storage through its operating-system-specific mount point.

On Linux, ~/ denotes the current user's home directory. On Windows, the equivalent home-directory notation depends on the environment in which the application runs.

---

## 5. Security Notes

Keep the following security considerations in mind when deploying the program.

### Password Strength

- Use a very strong master server password.
- Use a very strong master client password.
- Protect authentication key passwords and do not share them unnecessarily.
- Avoid reusing passwords across systems.

### Client Authorization

- New clients must be authorized by the server administrator.
- Authorization credentials are transferred out-of-band.
- Authentication keys are single-use and are invalidated when the server restarts or a client attempts to bootstrap.
- Disabling new-client bootstrapping when no new clients are expected reduces exposure to denial-of-service attacks against the enrollment process.

### Encryption at Rest

All keys are protected with data-at-rest encryption.

This helps protect stored key material if the underlying storage is accessed without authorization. It does not eliminate the need to secure passwords, restrict filesystem access, protect running processes, and maintain control over the server and client machines.

## Client Capacity and Scalability

The protocol is designed to support up to 2^512 clients in principle. However, this is a theoretical capacity, not a practical performance guarantee.

In practice, performance may begin to degrade as the number of clients approaches approximately 100–200, depending on the server's hardware, available memory, CPU performance, network bandwidth, and workload.

The actual number of clients the server can handle efficiently depends on usage patterns and system resources. For production deployments, test the server under realistic workloads to determine an appropriate client limit for your hardware.

### Psudo-TPM Compatibility

Psudo-TPM is optional and relies on Windows DPAPI. Its password-autofill integration is therefore Windows-only.

Linux users can operate the SFTP client without this optional component.

---

**Setup is complete** once the server is running, the client has been authorized, and the client has successfully completed bootstrapping.
