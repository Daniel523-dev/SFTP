# SFTP Program Setup Guide

This guide covers server and client installation, optional Psudo-TPM password autofill, client authorization, storage locations, and security considerations.

## Table of Contents

- [1. Server Setup](#1-server-setup)
- [2. Client Setup](#2-client-setup)
- [3. Authorizing a Client](#3-authorizing-a-client)
- [4. Storage Locations](#4-storage-locations)
- [5. Security Considerations](#5-security-considerations)
- [6. Client Capacity and Scalability](#6-client-capacity-and-scalability)

---

## 1. Server Setup

The server supports Windows and Linux.

### 1.1 Install Python and Dependencies

Install a compatible version of Python and ensure Python and pip are available from your terminal.

Install the required packages:

```shell
python -m pip install cryptography argon2-cffi numpy pyzmq blake3 zxcvbn
```

On Linux, use `python3` instead of `python` if required by your distribution.

### 1.2 Download the Server Files

Download the following files and place them together in the same directory:

- Encryption.py
- network.py
- server.py
- util.py

If the files are hosted in a Git repository, clone the repository or download and extract its source archive.

### 1.3 Configure Optional Psudo-TPM Password Autofill

**This step is optional and available only on Windows.** Skip it if you do not need password autofill.

Download the following files from the [Psudo-TPM repository](https://github.com/Daniel523-dev/Psudo-TPM):

- TPM.exe — the latest release.
- TPM_client.py — the corresponding client-side Python module.

Place both files in the same directory as the server files.

Install the additional dependencies:

```shell
python -m pip install zstandard pywin32
```

Psudo-TPM relies on the Windows Data Protection API (DPAPI), so this integration is not supported on Linux.

### 1.4 Start the Server

If you enabled Psudo-TPM, **launch TPM.exe before starting the server**. The TPM process must be running whenever the server starts or restarts.

Start the server from its installation directory:

```shell
python server.py
```

Follow the startup prompts to configure the server's passwords.

### 1.5 Configure the Master Server Password

When prompted, create a **strong, unique master server password**. This password protects the server's master key material and must not be reused for other accounts or services.

The server may also prompt for an authentication key password, which is used when authorizing new clients. This password is separate from the master server password.

If a sufficiently strong master password is not provided, the server disables new-client bootstrapping. This is useful when no additional clients are expected, as it reduces exposure to denial-of-service (DoS) attacks against the enrollment process.

If you intend to authorize new clients, ensure the server permits bootstrapping and follow [Section 3: Authorizing a Client](#3-authorizing-a-client).

The server is now configured.

---

## 2. Client Setup

The client supports Windows and Linux. Install the appropriate dependencies and filesystem integration for your operating system.

### 2.1 Install Python and Dependencies

Install a compatible version of Python and ensure pip is available.

**Windows**

```shell
python -m pip install watchdog pyzmq zxcvbn cryptography argon2-cffi blake3
```

**Linux**

```shell
python3 -m pip install fusepy pyzmq zxcvbn cryptography argon2-cffi blake3
```

The Linux client uses FUSE to expose remote storage through a filesystem mount point. Depending on your distribution, you may also need to install system-level FUSE packages and configure the required permissions.

### 2.2 Download the Client Files

Download the following files and place them together in the client directory:

- Encryption.py
- network.py
- client.py
- util.py

Also download the filesystem integration for your operating system:

- **Windows:** winfuse2.py
- **Linux:** vfs.py

If the files are hosted in a Git repository, clone the repository or download and extract its source archive.

### 2.3 Configure Optional Psudo-TPM Password Autofill

**This step is optional and available only on Windows.** Skip it if you do not need password autofill.

Download the following files from the [Psudo-TPM repository](https://github.com/Daniel523-dev/Psudo-TPM):

- TPM.exe — the latest release.
- TPM_client.py — the corresponding client-side Python module.

Place both files in the same directory as the client files.

Install the additional dependencies:

```shell
python -m pip install zstandard pywin32
```

Psudo-TPM relies on Windows DPAPI and is not supported on Linux. Linux users can run the client without this optional component.

### 2.4 Obtain Authorization from the Server Administrator

Before connecting for the first time, contact the server administrator and request authorization.

The administrator must provide an authentication key file and its corresponding password through a separate, trusted communication channel. This process is called **out-of-band authorization**.

Do not attempt to bootstrap the client until you have received both items. The administrator must coordinate the authorization process because authentication keys are single-use and can become invalid.

Follow [Section 3: Authorizing a Client](#3-authorizing-a-client) for the complete procedure.

---

## 3. Authorizing a Client

This section describes the initial authorization process for a new client. It requires coordination between the server administrator and the client user.

**Important:** Authentication keys are single-use. Coordinate key distribution and client bootstrapping so the key is not invalidated before it can be used.

### 3.1 Server Administrator: Prepare the Authentication Key

1. Restart the server to begin the authorization process.
2. When prompted, configure a secure authentication key password.
3. Locate the generated authentication key at:

   ```
   ./keys/auth_key
   ```

4. Transfer a copy of this file to the client user.
5. Communicate the corresponding authentication key password through a separate, trusted channel.

The authentication key password is distinct from the master server password. Keep it confidential, and never send the key and its password together through an untrusted channel.

### 3.2 Client User: Install the Authentication Key

1. Obtain the authentication key file and its password from the administrator.
2. Place the file in the client's current working directory — the directory from which you will launch the client.
3. Ensure the file is named:

   ```
   auth_key
   ```

4. Confirm that the key was issued for your authorization attempt and has not been invalidated.

### 3.3 Client User: Start the Client

If you enabled Psudo-TPM, **launch TPM.exe before starting the client**. The TPM process must be running whenever you launch or restart the client.

From the client installation directory, run:

**Windows**

```shell
python client.py
```

**Linux**

```shell
python3 client.py
```

Follow the startup prompts.

### 3.4 Client User: Configure the Master Client Password

When prompted, create a **strong, unique master client password**. This password protects the client's master key material.

Keep it secure and do not reuse the master server password or passwords from unrelated accounts.

### 3.5 Client User: Complete Bootstrapping

When prompted, enter the authentication key password provided by the administrator.

If the authentication key is valid and the bootstrapping process succeeds, the client will complete its initial authorization.

**Important:** During bootstrapping, the client overwrites its local auth_key file. Make sure the correct authorization key is in the working directory before starting the client.

### 3.6 Authentication Key Lifecycle

The server invalidates and discards its current authentication key whenever the server restarts or a client attempts to bootstrap.

As a result:

- Each authentication key is valid for a single bootstrapping attempt.
- Restarting the server may invalidate an unused key.
- Another client's bootstrapping attempt may invalidate the key before you use it.
- If a key becomes invalid, the administrator must generate and distribute a new one.

If bootstrapping fails because the key is invalid, contact the administrator before trying again. Do not assume that a previously issued key remains valid.

Once bootstrapping succeeds, the client has completed its initial authorization and can proceed to use the remote storage.

---

## 4. Storage Locations

The following table lists the default storage locations.

| Component | Operating System | Default Location |
|---|---|---|
| Server shared files | Windows or Linux | ~/Shared |
| Client mount point | Linux | /mnt/remote-storage |
| Client mount point | Windows | ~/mount |

The server stores shared files under ~/Shared. The client accesses remote storage through the mount point for its operating system.

On Linux, ~/ refers to the current user's home directory. On Windows, the effective home directory depends on the environment in which the application runs.

---

## 5. Security Considerations

### 5.1 Passwords

- Use strong, unique master server and master client passwords.
- Protect authentication key passwords and share them only with authorized users.
- Never reuse passwords across unrelated systems.
- Do not confuse the master server password, master client password, and authentication key password. They serve different purposes.

### 5.2 Client Authorization

- New clients must be authorized by the server administrator.
- Transfer authentication keys and their passwords through separate, trusted channels.
- Authentication keys are single-use and may be invalidated by server restarts or other bootstrapping attempts.
- Disable new-client bootstrapping when additional clients are not expected, where supported by the server configuration, to reduce exposure to enrollment-related DoS attacks.

### 5.3 Encryption at Rest

The program protects key material using data-at-rest encryption.

This helps protect stored keys if the underlying storage is accessed without authorization. However, it does not eliminate the need to protect passwords, restrict filesystem access, secure running processes, and maintain control over the server and client machines.

### 5.4 Psudo-TPM Compatibility

Psudo-TPM is an optional password-autofill integration that relies on Windows DPAPI.

- **Windows:** Psudo-TPM can be used if its files and dependencies are installed.
- **Linux:** The SFTP client can operate without Psudo-TPM.

When enabled, TPM.exe must be running before the server or client is launched.

---

## 6. Client Capacity and Scalability

The protocol is designed to support up to 2^512 clients in principle. This is a theoretical capacity, not a practical performance guarantee.

In practice, performance may begin to degrade as the number of clients approaches approximately 100–200. Actual performance depends on factors such as:

- CPU performance and available memory.
- Network bandwidth and latency.
- Client activity and workload.
- Server hardware and resource contention.

For production deployments, test the server under realistic workloads to determine an appropriate client limit for your environment.

---

## Setup Complete

Setup is complete when:

1. The server is running with its master password configured.
2. The client has received valid authorization credentials.
3. The client has successfully completed bootstrapping.
4. The client can access the remote storage through its configured mount point.

Psudo-TPM is optional and is not required for normal SFTP client operation.
