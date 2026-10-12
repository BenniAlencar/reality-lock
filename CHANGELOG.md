# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-11

### Added
- **5-Stage Finite State Machine**: Intent → Plan → Dispatch → Execution → Observed Evidence.
- **Cryptographic Execution Receipts**: Deterministic SHA-256 sealed receipts proving physical execution.
- **Default-Deny Policy Gate**: Human-in-the-loop and automated safeguards for destructive/external actions.
- **Physical Verifiers**:
  - `CommandVerifier`: Subprocess exit code, stdout hash, stderr inspection.
  - `FilesystemVerifier`: Pre- and post-execution SHA-256 diffs for verified disk mutations.
  - `HttpVerifier`: Status code and latency enforcement with token redaction.
- **Ecosystem Adapters**:
  - Python `@reality_locked` zero-boilerplate decorator.
  - Model Context Protocol (`McpToolGate`) proxy.
  - LangChain & LangGraph callback handler (`RealityLockCallbackHandler`).
  - CrewAI tool wrapper (`lock_crewai_tool`).
- **Rich Terminal CLI**:
  - `reality-lock info`: Brand, doctrine, and enterprise gateway.
  - `reality-lock verify-cmd`: Live execution with receipt table.
  - `reality-lock audit`: Executive terminal dashboard of intercepted actions.
  - `reality-lock init`: Zero-config initialization.
