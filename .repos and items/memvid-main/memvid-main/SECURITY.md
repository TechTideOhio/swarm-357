# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take security seriously at Memvid. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email us at: **security@memvid.com**

Include the following in your report:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

- **Acknowledgment**: We will acknowledge your report within 48 hours
- **Assessment**: We will assess the vulnerability and determine its severity
- **Fix Timeline**: Critical vulnerabilities will be addressed within 7 days
- **Disclosure**: We will coordinate with you on public disclosure timing
- **Credit**: We will credit you in our security advisories (unless you prefer anonymity)

### Scope

The following are in scope:
- Memory corruption vulnerabilities
- Data leakage from `.mv2` files
- Encryption bypass (when using `encryption` feature)
- Denial of service attacks
- Path traversal vulnerabilities

### Safe Harbor

We consider security research conducted in good faith to be authorized. We will not pursue legal action against researchers who:
- Act in good faith
- Avoid privacy violations
- Do not access or modify other users' data
- Report vulnerabilities promptly
- Give us reasonable time to fix issues before disclosure

## Security Best Practices

When using Memvid:

1. **File Permissions**: Set appropriate file permissions on `.mv2` files
2. **Encryption**: Use the `encryption` feature for sensitive data
3. **Validation**: Validate input before ingesting into memory
4. **Updates**: Keep Memvid updated to the latest version

## Security Features

Memvid includes several security features:

- **Checksums**: Blake3 checksums for data integrity
- **Signatures**: Ed25519 signatures for authenticity
- **Encryption**: Optional AES-256-GCM encryption (`.mv2e` capsules)
- **Crash Safety**: WAL-based recovery prevents corruption
