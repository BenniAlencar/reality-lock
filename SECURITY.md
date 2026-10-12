# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

The Reality Lock project takes agent safety, sandboxing, and security seriously.

If you believe you have discovered a vulnerability, policy bypass, or sandbox escape in Reality Lock:

1. **Do not create a public GitHub issue.**
2. Send an email to `security@bennios.dev` with:
   - Description of the vulnerability.
   - Proof of Concept (PoC) code or prompt that bypassed the policy gate.
   - Impact assessment.
3. The Benni OS Security Team (Tier-0 Cyber Sentinel) will acknowledge receipt within 24 hours.
4. Coordinated disclosure will follow once a patch is tested and verified.

## Zero-Trust Principles

Reality Lock operates under the principle of **Default-Deny**:
- Any unclassified external mutation must be paused for operator approval.
- Secrets, authorization headers, and sensitive environment variables are masked in all execution receipts.
