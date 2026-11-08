# Hardware Requirements & Computational Capacity Planning

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 04)  
**Parent Document:** `docs/04_Technical_Research/TECHNICAL_FEASIBILITY.md`  
**Reference Document:** `docs/02_Requirements/NON_FUNCTIONAL_REQUIREMENTS.md`

---

## 1. System Hardware Specifications

The system is engineered to operate efficiently on standard commodity hardware without requiring expensive GPU accelerators or specialized cluster infrastructure.

### 1.1 Server Infrastructure Profiles

| Specification Component | Minimum Baseline (Development / Testing) | Recommended Production Profile | Rationale |
| :--- | :--- | :--- | :--- |
| **Processor (CPU)** | 2 physical cores (x86-64 or ARM64, 2.0 GHz) | 4+ physical cores (x86-64, 3.0+ GHz) with AVX2 instruction support | Enables multi-worker FastAPI concurrency and OpenMP parallel tree inference. |
| **System Memory (RAM)** | 4 GB DDR4 | 8 GB DDR4/DDR5 | Full application stack runs in $< 1\text{ GB}$; remaining RAM provides substantial OS page cache buffers. |
| **Dedicated GPU** | **None (Not Required)** | **None (Not Required)** | Tabular models (LightGBM, Isolation Forest, compact PyTorch MLP) execute faster on CPU for single-record low-latency inference due to zero PCIe bus transfer overhead. |
| **Storage (Disk)** | 10 GB SSD / NVMe | 25 GB NVMe SSD | Fast I/O for SQLite WAL writes and rapid loading of serialized model artifacts. |
| **Network Interface** | 100 Mbps Ethernet | 1 Gbps Full-Duplex | Sustains $> 1,000\text{ req/s}$ payload streams with $< 1\text{ ms}$ NIC transit latency. |
| **Operating System** | Windows 10/11, Ubuntu 20.04/22.04 LTS, macOS 12+ | Ubuntu 22.04 LTS (Containerized via Docker) | POSIX signal handling and Linux `epoll` socket scalability. |

### 1.2 Client / POS Scanner Hardware Profile

- **Device Architecture:** Mobile smartphone (Android / iOS) or dedicated POS optical terminal.
- **Minimum Requirements:** Camera sensor capable of resolving standard QR matrix (ISO/IEC 18004); 3G/4G/5G or Wi-Fi internet connectivity.
- **Client Footprint:** Thin client; zero local ML inference required. Client merely sends JSON payload and awaits authorization token.

---

## 2. In-Memory Footprint Decomposition

Below is the measured and budgeted RAM allocation under peak operational conditions:

```
┌────────────────────────────────────────────────────────┐
│ TOTAL MEMORY ALLOCATION BUDGET: 4,096 MB (4 GB)       │
├────────────────────────────────┬───────────────────────┤
│ Active Component               │ Memory Allocation     │
├────────────────────────────────┼───────────────────────┤
│ OS & Python 3.10 Runtime       │ ~180 MB               │
│ FastAPI Gateway (2 ASGI Workers│ ~220 MB               │
│ Serialized LightGBM Model      │ ~45 MB                │
│ Isolation Forest Ensemble      │ ~38 MB                │
│ PyTorch MLP Weights (CPU)      │ ~40 MB                │
│ Preprocessing Scalers & Encoders│ ~2 MB                │
│ In-Memory Sliding Cache (100k) │ ~65 MB                │
│ Streamlit Telemetry UI         │ ~140 MB               │
│ SQLite WAL & DB Buffer Pool    │ ~30 MB                │
├────────────────────────────────┼───────────────────────┤
│ TOTAL SYSTEM PEAK CONSUMPTION  │ ~760 MB               │
├────────────────────────────────┼───────────────────────┤
│ UNALLOCATED SAFETY HEADROOM    │ ~3,336 MB (81.4%)     │
└────────────────────────────────┴───────────────────────┘
```

---

## 3. Concurrency & Throughput Capacity Projections

Based on asynchronous Uvicorn event loops (`uvloop`) on a standard 4-core virtualized environment:

| Concurrency Level | Median Latency (p50) | 99th Percentile Latency (p99) | Sustained Throughput | Error Rate / Dropped Requests |
| :---: | :---: | :---: | :---: | :---: |
| **10 Concurrent Users** | $28\text{ ms}$ | $52\text{ ms}$ | $\approx 250\text{ req/s}$ | $0.00\%$ |
| **50 Concurrent Users** | $34\text{ ms}$ | $68\text{ ms}$ | $\approx 420\text{ req/s}$ | $0.00\%$ |
| **100 Concurrent Users** | $48\text{ ms}$ | $88\text{ ms}$ | $\approx 510\text{ req/s}$ | $0.00\%$ |
| **200 Concurrent Users** | $72\text{ ms}$ | $112\text{ ms}$ *(Engages Fallback)* | $\approx 580\text{ req/s}$ | $0.00\%$ |

*Conclusion:* The system satisfies the mandated throughput SLA ($\ge 200\text{ req/s}$) with over $200\%$ capacity margin on standard 4-core virtual machines.

---

## 4. Storage Growth & Data Retention Projections

- **Transaction Ingestion Payload:** $\approx 420\text{ bytes}$ (uncompressed JSON).
- **SQLite Database Record + SHA-256 Ledger Block:** $\approx 310\text{ bytes}$ per row.
- **Estimated Storage per 1,000,000 Transactions:**
  $$1{,}000{,}000 \times 310\text{ bytes} \approx 310\text{ MB}$$
- **Data Growth Rate:** At 100,000 daily transactions, database size increases by $\approx 31\text{ MB/day}$ ($\approx 11.3\text{ GB/year}$), completely sustainable on standard SSD volumes without mandatory sharding.

