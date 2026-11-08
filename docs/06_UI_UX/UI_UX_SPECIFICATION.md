# UI/UX Specification: States, Accessibility & Interaction Guidelines

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 06)  
**Parent Document:** `docs/06_UI_UX/DESIGN_SYSTEM.md` | `docs/06_UI_UX/WIREFRAME_SPECIFICATION.md`  
**Accessibility Standard:** WCAG 2.1 Level AA Compliance

---

## 1. Interaction States Specification

Every screen and component in the interface must handle four discrete interaction states gracefully:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ LOADING      │ ──> │ SUCCESS      │ ──> │ EMPTY        │ ──> │ ERROR        │
│ Shimmer / Bar│     │ Clear Visuals│     │ Action Guide │     │ RFC 7807 Msg │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 1.1 Loading States
- **Live Stream Table:** When polling new data or connecting to the backend, table rows display a subtle CSS pulse shimmer rather than blanking out.
- **Simulator & Inference Actions:** Primary button `Simulate Payment Transaction` displays an inline spinner with label `Evaluating Features & Models...`. An execution timer runs continuously in milliseconds.
- **SHAP Waterfall Generation:** Renders a skeleton bar chart placeholder while the TreeExplainer computes polynomial Shapley values.
- **Ledger Verification:** Displays an animated progress bar indicating exact block verification counts: `Verifying Block 4,210 of 14,820...`.

### 1.2 Empty States
- **Live Stream Filter Mismatch:**
  - *Trigger:* User filters for `BLOCK` but zero blocked transactions exist in the active sliding window.
  - *Display:* Centered illustration with clear text:
    `No Blocked Transactions in Current Window. Showing normal baseline payment flow.`
    Action: `Clear Filters` link button.
- **Ledger Explorer Initial State:**
  - *Display:* Informational banner: `Genesis Block Initialized. Awaiting incoming payment events.`

### 1.3 Error & Exception States
- **Backend Disconnection / Offline Alert:**
  - If the FastAPI gateway or SQLite engine is unreachable, a persistent top toast banner appears:
    `⚠️ Fraud Gateway Unreachable (HTTP 503). Retrying connection in 3s... Standalone Mode Active.`
- **Schema Validation Errors (HTTP 422):**
  - Renders an RFC 7807 Problem Details toast highlighting the offending field:
    `Invalid Coordinate: Payer Latitude 142.5 exceeds permissible range [-90.0, 90.0].`
- **Fallback Circuit Breaker Banner:**
  - When inference exceeds $120\text{ ms}$ and triggers the fallback engine, the transaction row and detail view display an amber diagnostic badge:
    `⚡ Heuristic Fallback Engaged (Execution: 124ms > 120ms Threshold). Scored via rule heuristics.`

### 1.4 Success States
- **Chain Verification Success:**
  - Displays a solid emerald confirmation banner with checkmark:
    `✅ Ledger Integrity Certified: 14,820 / 14,820 Blocks Mathematically Intact (0.12s scan).`

---

## 2. Accessibility (a11y) & Usability Engineering

### 2.1 Colorblind-Safe Semantic Design (Deuteranopia & Protanopia)
To prevent misinterpretation by colorblind users, risk verdicts **never rely exclusively on color**:
1. **`APPROVE`:** Emerald Color (`#10B981`) + Checkmark Icon (`✓`) + Clear Text Label `[APPROVE]`.
2. **`CHALLENGE_MFA`:** Amber Color (`#F59E0B`) + Shield/Warning Icon (`🛡️`) + Clear Text Label `[CHALLENGE]`.
3. **`BLOCK`:** Crimson Color (`#EF4444`) + Octagonal Stop Icon (`🛑`) + Pulsing Indicator + Clear Text Label `[BLOCK]`.

### 2.2 Contrast Ratio Compliance (WCAG 2.1 AA)
- Text to Background contrast across all cards and tables strictly exceeds **$4.5:1$** for standard body text and **$7.0:1$** for large numeric KPI displays.
- High-contrast border dividers (`#475569`) separate adjacent dark panels to maintain clear visual boundaries.

### 2.3 Keyboard Navigation & Screen Reader Support
- All interactive controls (buttons, preset selectors, sliders) are reachable via standard keyboard `Tab` sequences with visible indigo focus outlines (`#6366F1`).
- SHAP feature charts provide accessible tabular data equivalents for screen readers.

