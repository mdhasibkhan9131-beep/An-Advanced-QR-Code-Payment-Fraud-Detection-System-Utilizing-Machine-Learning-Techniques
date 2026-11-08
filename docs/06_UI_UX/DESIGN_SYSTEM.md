# Enterprise Design System: Fintech Precision

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 06)  
**Parent Document:** `docs/06_UI_UX/SCREEN_INVENTORY.md`  
**Design Philosophy:** High-Density Telemetry, Instant Cognitive Clarity, Dark-First Cyber Aesthetic

---

## 1. Color Palette & Semantic Tokens

The design system prioritizes high-contrast visual hierarchy designed for low eye-strain during extended operations room shifts:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CORE COLOR PALETTE                              │
├───────────────────┬─────────────┬───────────┬───────────────────────────────┤
│ Token Name        │ Hex Code    │ CSS Var   │ Purpose                       │
├───────────────────┼─────────────┼───────────┼───────────────────────────────┤
│ `bg-canvas`       │ `#0F172A`   │ `--bg-0`  │ Main application background   │
│ `bg-surface`      │ `#1E293B`   │ `--bg-1`  │ Card panels & sidebar         │
│ `bg-surface-hover`│ `#334155`   │ `--bg-2`  │ Table row hover / active tab  │
│ `border-subtle`   │ `#475569`   │ `--bdr`   │ Component dividers & borders  │
│ `text-primary`    │ `#F8FAFC`   │ `--tx-1`  │ Primary headings & values     │
│ `text-secondary`  │ `#94A3B8`   │ `--tx-2`  │ Field labels & metadata       │
│ `text-muted`      │ `#64748B`   │ `--tx-3`  │ Placeholders & disabled text  │
├───────────────────┼─────────────┼───────────┼───────────────────────────────┤
│ `risk-approve`    │ `#10B981`   │ `--clr-ok`│ APPROVE verdict (Emerald)     │
│ `risk-challenge`  │ `#F59E0B`   │ `--clr-wn`│ CHALLENGE_MFA verdict (Amber) │
│ `risk-block`      │ `#EF4444`   │ `--clr-dg`│ BLOCK verdict (Crimson)       │
│ `brand-accent`    │ `#6366F1`   │ `--clr-ac`│ Primary CTA & focus rings     │
│ `telemetry-cyan`  │ `#06B6D4`   │ `--clr-tm`│ Latency counters & XAI plots  │
└───────────────────┴─────────────┴───────────┴───────────────────────────────┘
```

### High-Contrast Risk Pill Styling:
- **`APPROVE` Pill:**
  - Background: `rgba(16, 185, 129, 0.15)`
  - Border: `1px solid #10B981`
  - Text: `#34D399` (Bold, Uppercase)
- **`CHALLENGE_MFA` Pill:**
  - Background: `rgba(245, 158, 11, 0.15)`
  - Border: `1px solid #F59E0B`
  - Text: `#FBBF24` (Bold, Uppercase)
- **`BLOCK` Pill:**
  - Background: `rgba(239, 68, 68, 0.18)`
  - Border: `1px solid #EF4444`
  - Text: `#F87171` (Bold, Uppercase, Pulsing Dot)

---

## 2. Typography & Font Hierarchy

- **UI Headings & Body:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, `sans-serif`.
- **Numerical Telemetry & Hash Codes:** `JetBrains Mono`, `Fira Code`, `Consolas`, `monospace`.

| Hierarchy Level | Font Size | Weight | Line Height | Usage |
| :--- | :---: | :---: | :---: | :--- |
| **Display H1** | $28\text{ px}$ | Bold (700) | $36\text{ px}$ | Screen Titles (e.g., Live Telemetry Stream) |
| **Section H2** | $22\text{ px}$ | Semi-Bold (600) | $28\text{ px}$ | Subsystem Headers & Panel Titles |
| **Card H3** | $18\text{ px}$ | Medium (500) | $24\text{ px}$ | KPI Card Titles & Modal Headers |
| **Body Primary**| $14\text{ px}$ | Regular (400) | $20\text{ px}$ | Form Labels, Descriptions, Table Data |
| **Mono Values** | $13\text{ px}$ | Medium (500) | $18\text{ px}$ | Transaction IDs, Block Hashes, GPS Coords |
| **Micro Caption**| $11\text{ px}$ | Regular (400) | $16\text{ px}$ | Timestamps, Footers, Sub-labels |

---

## 3. Spacing & Grid System (8pt Base Grid)

All layout margins, paddings, and component alignments derive strictly from an 8-point base grid:
- `space-1`: $4\text{ px}$ (tight internal tag padding)
- `space-2`: $8\text{ px}$ (spacing between input label and field)
- `space-3`: $12\text{ px}$ (button internal padding)
- `space-4`: $16\text{ px}$ (standard card internal padding)
- `space-6`: $24\text{ px}$ (gutter between grid cards)
- `space-8`: $32\text{ px}$ (major section separation)

---

## 4. Reusable UI Components

### 4.1 KPI Metric Widget
```
┌──────────────────────────────────────────────┐
│ THROUGHPUT (REQ/S)                       ⚡  │
│ 342.5                                        │
│ ↑ +12% from trailing 1h   •  p95: 58.4 ms   │
└──────────────────────────────────────────────┘
```
- Background: `#1E293B`, Border: `1px solid #334155`, Border-Radius: `8px`.
- Value rendered in Large Display Semi-Bold ($28\text{ px}$).

### 4.2 Three-Way Risk Dial Gauge
Displays concurrent risk contributions:
- **Left Arc:** Supervised Classifier Probability $P_{\text{fraud}} \in [0, 1]$ (Blue arc).
- **Middle Arc:** Unsupervised Anomaly Score $S_{\text{anomaly}} \in [0, 1]$ (Purple arc).
- **Center Hero Dial:** Blended Composite Score $S_{\text{composite}} \in [0, 1]$ (Color shifts dynamically: Green $<0.30 \to$ Amber $\to$ Red $>0.70$).

### 4.3 High-Density Interactive Data Table
- Alternating row background for fast scanning.
- Fixed table header with sticky sort indicators.
- Truncated hash codes with one-click copy tooltips.
- Visual micro-bars depicting transaction value and distance relative to normal bounds.

