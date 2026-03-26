# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.12.x  | Yes       |
| 2.11.x  | Yes       |
| < 2.11  | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in PromptBIM, please report it responsibly:

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email: michael@realitymatrix.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a detailed response within 5 business days.

## Security Measures

### API Key Protection

- API keys are stored in `.env` files (never committed to git)
- `.env` is listed in `.gitignore`
- The health check system warns if `.env` has incorrect permissions
- Path injection protection in PythonBridge (Swift-Python IPC)

### Dependency Auditing

- `pip-audit` runs in CI on every push to `main`
- Known vulnerabilities are tracked and documented
- `requirements-frozen.txt` pins all dependency versions

### Input Validation

- All land parcel inputs are validated via Pydantic schemas
- File path inputs are sanitized to prevent path traversal
- MCP server validates all tool inputs before processing

### CI/CD Security

- GitHub Actions with minimal permissions
- No secrets in workflow files
- Concurrency controls prevent parallel deployments

## Known Advisories

| CVE | Package | Status |
|-----|---------|--------|
| CVE-2026-4539 | pygments 2.19.2 | Acknowledged, no fix available yet |

---

*SECURITY.md v1.0 | 2026-03-27 | PromptBIM v2.12.0*
