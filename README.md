<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0D0D0D,50:003816,100:00FF66&height=200&section=header&text=reality-lock&fontSize=56&fontColor=ffffff&fontAlignY=38&desc=Deterministic%20Zero-Trust%20%26%20Observed%20Physical%20Evidence%20Engine%20for%20AI%20Agents&descAlignY=58&descSize=16&animation=fadeIn" width="100%"/>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=20&duration=3000&pause=800&color=00FF66&center=true&vCenter=true&multiline=true&repeat=true&width=900&height=80&lines=Deterministic+Zero-Trust+for+AI+Agents.;Eliminate+the+Agent+Hallucination+of+Done.;No+Physical+Evidence%2C+It+Did+Not+Happen.;Benni+Master+OS+Kernel+v9.4+%E2%80%94+Skill+62+Native." alt="Typing SVG" />

<br/><br/>

[![CI](https://github.com/BenniAlencar/reality-lock/actions/workflows/ci.yml/badge.svg)](https://github.com/BenniAlencar/reality-lock/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-29%20Passed-00FF66?style=for-the-badge&logo=pytest&logoColor=0D0D0D)](#-test-suite--verification)
[![Python](https://img.shields.io/badge/Python-3.10+-00FF66?style=for-the-badge&logo=python&logoColor=0D0D0D)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Zero--Trust%20Gate-00FF66?style=for-the-badge&logo=anthropic&logoColor=0D0D0D)](https://modelcontextprotocol.io/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-0D0D0D?style=for-the-badge&logo=apache&logoColor=00FF66)](LICENSE)
[![Part of Benni OS](https://img.shields.io/badge/Part%20of-Benni%20OS-0D0D0D?style=for-the-badge&logo=githubactions&logoColor=00FF66)](https://github.com/BenniAlencar)

<br/>

> **"If an action does not yield observed, physical evidence — exit code 0, matching disk byte hash, HTTP status confirmation — it did not happen."**

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>

</div>

<br/>

## ⭐ What Is reality-lock?

**reality-lock** is the deterministic zero-trust execution and physical verification engine of the **[Benni OS](https://github.com/BenniAlencar)** ecosystem. It provides the missing cryptographic guardrail layer for autonomous AI agents, LangChain/CrewAI swarms, and Model Context Protocol (MCP) tool callers.

Every existing agent framework lets the LLM announce success based on statistical tokens alone. When an LLM claims *"I updated the database schema and deployed the microservice"*, it may have suffered a silent subprocess crash, an unauthorized permission rejection, or an unwritten buffer.

`reality-lock` enforces the **Iron Reality Lock Doctrine**: separating Intent, Plan, Policy Gate, Dispatch, Execution, and Cryptographically Observed Evidence into a non-bypassable finite-state machine.

```
   Autonomous Agent / MCP Tool Caller / LangChain / CrewAI
                             ↓
             [ @reality_locked(risk=MUTATION) ]
                             ↓
    ┌─────────────────────────────────────────────────────────┐
    │                      reality-lock                       │
    │                                                         │
    │  ┌───────────────────────┐   ┌───────────────────────┐  │
    │  │  Default-Deny Gate    │   │  Pre-Execution Seal   │  │
    │  │  Policy / HITL Check  │ → │  Payload SHA-256      │  │
    │  └───────────────────────┘   └───────────────────────┘  │
    └─────────────────────────────────────────────────────────┘
                             ↓
         Physical Execution (Subprocess / Disk / Network)
                             ↓
    ┌─────────────────────────────────────────────────────────┐
    │  Observed Evidence Verifier                             │
    │  • Subprocess: Real Exit Code == 0 & Stdout Digest      │
    │  • Filesystem: Pre vs Post Disk Byte SHA-256 Diff       │
    │  • Ledger: Tamper-Evident SHA-256 Execution Receipt     │
    └─────────────────────────────────────────────────────────┘
                             ↓
         Verified Execution Receipt or Hard Rejection
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## ⚡ Core Doctrine

> These are not optional configuration flags. These are architecture laws.

| ☔ Principle | 🔧 Implementation |
|---|---|
| **The Reality Lock Law** | If an action produces no observed physical artifact (exit code 0, disk hash diff, HTTP 2xx), `verified = False`. Zero exceptions. |
| **Default-Deny Policy Gate** | Every mutating tool call is denied until explicitly verified against risk threshold and operator policy. |
| **5 Iron States** | Transitions strictly enforce: `INTENT` → `PLAN` → `POLICY_GATE` → `DISPATCH` → `OBSERVED_EVIDENCE`. |
| **Cryptographic Sealing** | Every execution generates a sealed JSON receipt signed with an immutable SHA-256 digest. |
| **Zero-Token Latency Overhead** | Pure deterministic Python (< 1ms overhead). No expensive secondary LLM calls required to verify reality. |
| **Subprocess Integrity** | Direct OS execution interceptor captures true exit codes, runtime duration, and truncated stdout digests. |
| **Filesystem Proof** | Pre-flight vs. post-flight byte comparison ensures bytes physically landed on disk before declaring success. |

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 🚀 Quick Start

### 1. Installation

```bash
# Clone
git clone https://github.com/BenniAlencar/reality-lock
cd reality-lock

# Install
pip install -e ".[dev]"
```

### 2. Protect any Python Tool or Function

```python
from reality_lock import reality_locked, RiskLevel

# Read-only actions run smoothly with deterministic receipt logging
@reality_locked(risk=RiskLevel.READ_ONLY)
def get_system_health():
    return {"cluster": "us-east-1", "nodes": 12, "status": "nominal"}

# High-risk side effects require operator approval in interactive mode
@reality_locked(risk=RiskLevel.EXTERNAL_MUTATION)
def deploy_canary(service: str, version: str):
    # Denied automatically if policy rejects or operator declines
    return f"Canary deployed: {service} v{version}"
```

### 3. Verify Real Subprocess Execution

```python
from reality_lock import RealityLockEngine, RiskLevel

engine = RealityLockEngine()

# Executes command and verifies real exit code and stdout digest
receipt = engine.lock_command(["pytest", "tests", "-v"], risk_level=RiskLevel.READ_ONLY)

print("Observed Exit Code:", receipt.evidence_data["exit_code"])
print("Verified by Reality Lock:", receipt.verified)
print("Receipt Hash:", engine.ledger[-1].receipt_hash)
```

### 4. Prove Real Disk Mutations with SHA-256 Diffs

```python
from pathlib import Path
from reality_lock import RealityLockEngine

engine = RealityLockEngine()

# Pre-checks disk state, executes write, and verifies post-mutation SHA-256 hash
saved_path = engine.lock_file_write(
    filepath=Path("dist/release_manifest.json"),
    content='{"version": "1.0.0", "status": "verified"}',
    intent="Write sealed release manifest",
)
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 🧠 Skill 62 & 01 — The 5 Iron States of Execution

Derived from **Benni Master OS Skill 62 (Quality & Safety OS)** and **Skill 01 (Operator Core Contract)**, `reality-lock` replaces blind agent executions with a strict finite-state engine:

| State | Responsibility | Verification Trigger |
|---|---|---|
| **1. INTENT** | What the agent claims it wants to accomplish | Natural language intent captured in receipt |
| **2. PLAN** | Target parameters, target files, shell args | Arguments serialized & payload SHA-256 digested |
| **3. POLICY GATE** | Default-Deny evaluation against risk profile | Auto-denies unauthorized destructive operations |
| **4. DISPATCH** | Pre-execution physical state captured | Disk snapshots taken; subprocess pipe armed |
| **5. OBSERVED EVIDENCE** | Physical inspection of actual system change | Exit code == 0, stdout hash, disk byte diff verified |

```bash
# Terminal execution check with interactive receipt audit
$ reality-lock verify-cmd "python -c 'print(42)'"

🔒 Reality Lock Execution Gate
   • Intent: Subprocess Command Execution
   • Command: python -c 'print(42)'
   • Exit Code: 0
   • Runtime: 38.2 ms
   • SHA-256 Digest: 9f83...
   ✔ OBSERVED EVIDENCE SEALED: verified=True
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 🔌 Model Context Protocol (MCP) Zero-Trust Gate

The Anthropic **Model Context Protocol (MCP)** gives LLMs access to databases, cloud infrastructure, and shell tools. However, MCP clients execute tool calls with raw, uninspected permissions.

`McpToolGate` acts as a zero-trust proxy for any MCP tool:

```python
from reality_lock import McpToolGate, PolicyGate, RiskLevel

# Configure zero-trust: mutate operations auto-denied unless explicitly approved
gate = McpToolGate(
    policy_gate=PolicyGate(mode="auto_deny", require_approval_threshold=RiskLevel.EXTERNAL_MUTATION)
)

# Intercept and gate MCP tools/call
mcp_response = gate.handle_call(
    tool_name="delete_database_table",
    arguments={"table": "customers"},
    tool_implementation=actual_tool_function,
)

# Returns standard MCP JSON-RPC payload with Reality Lock verification metadata
print(mcp_response["isError"])  # True
print(mcp_response["content"][0]["text"]) # "[REALITY-LOCK ERROR] Operator declined or policy denied"
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 🧩 Framework Integrations

### LangChain & LangGraph
```python
from reality_lock import RealityLockCallbackHandler, RealityLockEngine
from langchain.agents import AgentExecutor

engine = RealityLockEngine()
handler = RealityLockCallbackHandler(engine=engine)

# Intercepts every LLM tool call with zero-trust receipts
agent_executor.invoke({"input": "Run system diagnostics"}, config={"callbacks": [handler]})
```

### CrewAI
```python
from reality_lock import lock_crewai_tool, RiskLevel

# Wrap any CrewAI tool with reality-locked physical verification
protected_tool = lock_crewai_tool(my_destructive_tool, risk=RiskLevel.EXTERNAL_MUTATION)
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 📊 Reality Lock vs. Conventional Guardrails

| Capability | NeMo Guardrails / Guardrails AI | Llama Guard | **reality-lock** |
|---|:---:|:---:|:---:|
| **Inspection Target** | Text & Prompts only | Prompt Classifiers | **Physical System Reality** |
| **Catches Exit Code Lies** | ❌ No | ❌ No | **✅ Yes (`CommandVerifier`)** |
| **Proves Disk File Changes** | ❌ No | ❌ No | **✅ Yes (`FilesystemVerifier`)** |
| **Cryptographic Sealed Receipts** | ❌ No | ❌ No | **✅ Yes (SHA-256 Digest)** |
| **Default-Deny Tool Gate** | ⚠️ Partial | ❌ No | **✅ Yes (Strict FSM)** |
| **MCP Native Proxy** | ❌ No | ❌ No | **✅ Yes (`McpToolGate`)** |
| **Latency / Memory Overhead** | Heavy (runs secondary LLM) | Heavy (7B model) | **Ultralight (< 1ms, Zero LLM)** |

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 💻 Terminal CLI & Audit Dashboard

`reality-lock` ships with an interactive command-line suite:

```bash
# Display brand, version, and architecture doctrine
reality-lock info

# Verify any command in the terminal and inspect the cryptographic receipt
reality-lock verify-cmd "python -c 'print(42)'"

# Print an executive audit dashboard of all intercepted actions
reality-lock audit .reality_ledger.jsonl

# Generate initial zero-trust configuration
reality-lock init
```

### Cryptographic Receipt Artifact

Every execution generates an immutable JSON receipt:

```json
{
  "receipt_id": "rcpt_7f3a9e120b4a",
  "intent": "Deploy microservice canary",
  "action_name": "k8s_deploy",
  "risk_level": "external_mutation",
  "state": "observed_evidence",
  "started_at": "2026-10-12T04:25:00.120+00:00",
  "completed_at": "2026-10-12T04:25:00.450+00:00",
  "duration_ms": 330.12,
  "payload_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "evidence": {
    "exit_code": 0,
    "stdout_snippet": "deployment.apps/canary created",
    "stdout_sha256": "4a7d2b8...",
    "duration_ms": 328.5
  },
  "verified": true,
  "policy_approval": {"status": "approved", "timestamp": 1791763500.2},
  "receipt_hash": "9c1b3f6a27e8d19..."
}
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 🗂️ Project Structure

```
reality-lock/
├── reality_lock/
│   ├── __init__.py               # Public API exports
│   ├── version.py                # Version & Benni OS v9.4 doctrine
│   ├── core/
│   │   ├── engine.py             # RealityLockEngine runtime
│   │   ├── states.py             # 5 Iron States enum & FSM
│   │   └── models.py             # ActionIntent, ExecutionReceipt, RiskLevel
│   ├── gates/
│   │   └── policy.py             # Default-Deny PolicyGate & approvals
│   ├── verifiers/
│   │   ├── command.py            # Subprocess real execution verifier
│   │   └── filesystem.py         # SHA-256 pre/post disk diff verifier
│   ├── mcp/
│   │   └── gate.py               # McpToolGate zero-trust proxy
│   ├── integrations/
│   │   ├── langchain.py          # RealityLockCallbackHandler
│   │   └── crewai.py             # lock_crewai_tool wrapper
│   └── cli/
│       └── main.py               # reality-lock info / verify-cmd / audit
├── tests/
│   ├── test_engine.py
│   ├── test_verifiers.py
│   ├── test_policy.py
│   ├── test_mcp_gate.py
│   ├── test_integrations.py
│   └── test_cli.py
├── pyproject.toml
├── LICENSE
└── README.md
```

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 🛠️ Development & Test Suite

```bash
git clone https://github.com/BenniAlencar/reality-lock
cd reality-lock
pip install -e ".[dev]"

# Run full test suite with verbose traceback
pytest tests -v --tb=short
```

**Requirements:**
- Python 3.10, 3.11, or 3.12
- Zero external runtime dependencies for core verification
- Click & Rich for terminal auditing

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 🤝 Contributing

All contributions are welcome. Priority tracks:
- Verifiers for Docker, Kubernetes, and Cloud SDKs
- Protocol bridges for additional agent frameworks
- Pre-built policy templates for enterprise compliance

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development guidelines.

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/dark.png" width="100%"/>

## 🌐 Benni OS Ecosystem

| Product | Repo | Role | Status |
|---|---|---|---|
| 🧠 **Benni Master OS** | [benni-os/Benni-Master-OS](https://github.com/benni-os/Benni-Master-OS) | General Brain — sovereign multi-agent orchestrator | 🟢 Live |
| ⚡ **Project Adam** | [benni-os/Project-Adam](https://github.com/benni-os/Project-Adam) | Local operator runtime & agent swarm coordinator | 🟢 Ativo |
| 🔒 **reality-lock** | [BenniAlencar/reality-lock](https://github.com/BenniAlencar/reality-lock) | Deterministic zero-trust & execution evidence — you are here | 🟢 Live |
| 🧠 **agent-memory-mesh** | [BenniAlencar/agent-memory-mesh](https://github.com/BenniAlencar/agent-memory-mesh) | Bi-temporal state graph & lossless context compression | 🟢 Live |
| 🔌 **Operator Gateway** | [benni-os/benni-operator-gateway](https://github.com/benni-os/benni-operator-gateway) | Open-source MCP HTTP gateway & federation hub | 🟢 MIT |
| 🐍 **mcp-forge** | [benni-os/mcp-forge](https://github.com/benni-os/mcp-forge) | FastAPI-style Python MCP framework | 🟢 PyPI |
| ⚡ **benni-nexus** | [benni-os/benni-nexus](https://github.com/benni-os/benni-nexus) | LLM gateway — strategy routing & fallback | 🟢 npm |
| 🔥 **benni-inference-engine** | [benni-os/benni-inference-engine](https://github.com/benni-os/benni-inference-engine) | GPU+CPU hybrid inference for MoE models | 🔥 Building |
| 🛠️ **Benni Control Plane** | MCP on Railway | Quad-Mesh State, RLS isolation & memory layer | 🟢 Live |
| 🤖 **Project Benjamin** | [benni-os/Project-Benjamin](https://github.com/benni-os/Project-Benjamin) | Sovereign mechanical execution arm & zero-token I/O | 🔥 Hot |
| 🌌 **Project Genesis** | [benni-os/benni-os-genesis](https://github.com/benni-os/benni-os-genesis) | Sovereign IDE & Execution Harness (Creative Studio + MONOMO) | 🟢 Live |
| 🛍️ **Modo Operador** | [benni-os/modo-operador](https://github.com/benni-os/modo-operador) | Produto BR — R$97 | 🟢 Live |

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00FF66,50:003816,100:0D0D0D&height=120&section=footer" width="100%"/>

<div align="center">

**reality-lock** — *Deterministic Zero-Trust Execution Engine by [Benni OS](https://github.com/BenniAlencar)*

`REALITY_LOCK` • `SKILL_62_NATIVE` • `ZERO_TRUST_MCP` • `OBSERVED_EVIDENCE` • `APACHE_2.0`

Built by [Benni Alencar](https://github.com/BenniAlencar)

</div>
