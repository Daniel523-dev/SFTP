# Encryption.py

`Encryption.py` is a comprehensive Python utility module that provides a high-level, easy-to-use interface for common cryptographic operations. It wraps the powerful `cryptography` library along with `argon2` and optionally `blake3` to handle hashing, key derivation, symmetric/asymmetric encryption, digital signatures, and certificate management.

## Features

* **Hashing & Key Derivation (KDF)**
* Fast hashing using `blake3` (with a fallback to `sha3_256`/`shake_256`).
* Secure Key Derivation using `argon2id` with configurable cost levels (`kdf_fast`, `kdf_slow`, etc.).


* **Symmetric Encryption**
* **AES-CTR** for streaming/large data encryption.
* **AES-GCM** for authenticated symmetric encryption.
* **ChaCha20-Poly1305** for fast, secure authenticated encryption.


* **Asymmetric Cryptography**
* Key Exchange (ECDH) via **X25519** and **X448**.
* Digital Signatures via **Ed25519** and **Ed448**.


* **Public Key Infrastructure (PKI) & TLS**
* Generate self-signed TLS certificates.
* Create Certificate Authorities (CAs).
* Generate, sign, and validate X.509 certificates.
* Flexible key loading (PEM, DER, Raw) with automatic format detection.



## Requirements

To use this module, you need to install the following dependencies:

```bash
pip install cryptography argon2-cffi
```

**Optional (but recommended for performance):**
```bash
pip install blake3
```
*If `blake3` is not installed, the module will automatically fall back to standard library `hashlib` (SHA-3) and `HKDF`.*

## Usage Examples

### Hashing and Key Derivation

```python
import Encryption as enc

# Generate a fast hash

digest = enc.HASH(b"my_data", l=32, hex=True)

# Derive a strong key from a password

salt = os.urandom(16)
key = enc.kdf_fast(b"my_password", salt)
```

### Symmetric Encryption (AES-GCM)

```python
import Encryption as enc

key = b"super_secret_key_32_bytes_long!!"
data = b"Sensitive information"

# Encrypt

ciphertext = enc.encryptGCM(data, key, secure_kdf=True)

# Decrypt

plaintext = enc.decryptGCM(ciphertext, key, secure_kdf=True)
```

### Digital Signatures (Ed25519)

```python
import Encryption as enc

# Generate key pair

private_key, public_key = enc.gen_ed25519()

data = b"Data to be signed"

# Sign the data (returns signature + original data appended)

signed_data = enc.ed25519_sign(private_key, data)

# Verify the data (returns the original data if valid)

verified_data = enc.ed25519_verify(public_key, signed_data)
```

### Key Exchange (X25519)

```python
import Encryption as enc

# Alice generates keys

alice_priv, alice_pub = enc.gen_x25519()

# Bob generates keys

bob_priv, bob_pub = enc.gen_x25519()

# Both derive the same shared secret

alice_shared = enc.shared_secret(alice_priv, bob_pub)
bob_shared = enc.shared_secret(bob_priv, alice_pub)

assert alice_shared == bob_shared
```

### Generating a TLS Certificate

```python
import Encryption as enc

enc.generate_tls(
cert_path="cert.pem",
key_path="key.pem",
common_name="localhost",
valid_days=365
)
```

## Security Notes

* **KDF Levels:** The module uses a predefined dictionary (`KDF_LEVELS`) to scale the time and memory costs of Argon2 hashing. Higher levels are more secure against brute force but take longer to compute.
* **Randomness:** Uses `os.urandom()` and the `secrets` module for secure random number and ID generation.
* **Overkill Mode:** Asymmetric generation functions (`gen_x25519`, `gen_ed25519`, `gen_keys`) include an `overkill=True` flag that upgrades the algorithms from 255-bit (X25519/Ed25519) to 448-bit (X448/Ed448) for extreme security margins.
