# Reality Lock — Architecture Specification

**Doctrine:** Benni Master OS v9.4 — Skill 62 (Quality & Safety OS / Reality Lock)

---

## 1. System Overview

`reality-lock` eliminates the "Agent Hallucination of Done" by forcing every agent action through a strict 5-state finite-state machine (**Intent → Plan → Dispatch → Execution → Observed Evidence**) backed by Default-Deny policy gates, physical verifiers, and SHA-256 sealed `ExecutionReceipt` records.

```text
  LangChain / CrewAI / MCP Clients / @reality_locked Python Functions
         │
         ├──► RealityLockEngine.execute / lock_command
         └──► McpToolGate (JSON-RPC 2.0 Zero-Trust Gate)
                       │
                       ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                            reality-lock                             │
  │                                                                     │
  │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────┐  │
  │  │ Default-Deny      │  │  5-State Engine   │  │ Physical        │  │
  │  │ PolicyGate        │─►│  INTENT -> PLAN   │─►│ Verifiers       │  │
  │  │ • RiskLevel       │  │  -> DISPATCH      │  │ • CommandVerifier│ │
  │  │ • Human Approval  │  │  -> EXECUTION     │  │ • Filesystem    │  │
  │  └───────────────────┘  └───────────────────┘  │ • HttpVerifier  │  │
  │                                                └─────────────────┘  │
  │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────┐  │
  │  │ Cryptographic     │  │  Framework        │  │ Tools & CLI     │  │
  │  │ ExecutionReceipt  │  │  Adapters         │  │ • doctor        │  │
  │  │ • SHA-256 Seal    │  │  • @reality_locked│  │ • bench_matrix  │  │
  │  │ • Tamper Check    │  │  • LangChain/Crew │  │ • verify-cmd    │  │
  │  └───────────────────┘  └───────────────────┘  └─────────────────┘  │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

| Module | Responsibility |
|---|---|
| `reality_lock/core/states.py` | `ExecutionState` (5 iron states), `RiskLevel`, `PolicyDecision` |
| `reality_lock/core/policy.py` | `PolicyGate` enforcing Default-Deny and human-in-the-loop approval thresholds |
| `reality_lock/core/receipt.py` | `ExecutionReceipt` with SHA-256 sealing and `is_tampered()` verification |
| `reality_lock/core/engine.py` | `RealityLockEngine` coordinating policy, dispatch, verifiers, and JSONL ledger |
| `reality_lock/verifiers/` | Physical evidence verifiers (`command.py`, `filesystem.py`, `http.py`, `base.py`) |
| `reality_lock/adapters/` | `@reality_locked` decorator, `McpToolGate`, `RealityLockCallbackHandler`, `lock_crewai_tool` |
| `reality_lock/tools/` | `doctor.py` zero-trust probe and `bench_matrix.py` receipt throughput matrix |
| `reality_lock/cli/main.py` | Click + Rich CLI (`info`, `verify-cmd`, `audit`, `init`, `doctor`, `matrix`) |

---

## 3. Verification Gates

- `scripts/gate_reality_lock_runner.py`: Fail-closed gate verifying Default-Deny policy enforcement, `OBSERVED_EVIDENCE` sealing, missing-file rejection, and receipt tamper detection.
- `scripts/benchmark_receipt_throughput.py`: In-memory vs JSONL receipt sealing throughput benchmark.
