"""
Streamlit UI Prototype: Advanced QR Code Payment Fraud Detection System
Demonstrates design system, live telemetry, interactive attack simulator,
XAI feature attributions, and cryptographic ledger verification.
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import hashlib

# ---------------------------------------------------------
# Page Configuration & Design System Injector
# ---------------------------------------------------------
st.set_page_config(
    page_title="QR Fraud Surveillance Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyber-Fintech Dark Theme CSS
CUSTOM_CSS = """
<style>
    /* Dark Canvas Base */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    /* Cards & Containers */
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700;
        color: #F8FAFC !important;
        font-family: 'JetBrains Mono', monospace;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600;
        color: #94A3B8 !important;
        letter-spacing: 0.5px;
    }
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    /* Verdict Pills */
    .pill-approve {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid #10B981;
        color: #34D399;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    .pill-challenge {
        background-color: rgba(245, 158, 11, 0.15);
        border: 1px solid #F59E0B;
        color: #FBBF24;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    .pill-block {
        background-color: rgba(239, 68, 68, 0.18);
        border: 1px solid #EF4444;
        color: #F87171;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    /* Monospace elements */
    .mono-code {
        font-family: 'JetBrains Mono', monospace;
        color: #38BDF8;
        font-size: 12px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation & System Telemetry Header
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ QR Fraud Surveillance")
    st.markdown("<span class='mono-code'>[● LIVE SYSTEM: ONLINE]</span>", unsafe_allow_html=True)
    st.caption("Active Model: **LightGBM_v1.0.0**")
    st.caption("Environment: **Standalone Offline**")
    st.divider()

    navigation = st.radio(
        "Navigation",
        [
            "1. Live Telemetry & Feed",
            "2. Transaction Detail & XAI",
            "3. Fraud Vector Simulator",
            "4. Benchmark Scoreboard",
            "5. Ledger & Audit Explorer"
        ],
        index=0
    )

    st.divider()
    st.markdown("**System Health**")
    st.markdown("• Core Latency (p95): `54.2 ms`")
    st.markdown("• Ingestion Throughput: `342 req/s`")
    st.markdown("• Cache Status: `In-Memory TTL`")

# ---------------------------------------------------------
# View 1: Live Telemetry & Transaction Stream
# ---------------------------------------------------------
if navigation == "1. Live Telemetry & Feed":
    st.title("⚡ Live Telemetry & Transaction Stream")
    st.caption("Real-time fraud surveillance and instant authorization triage.")

    # KPI Banner
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Throughput", "342.5 req/s", "+12%")
    col2.metric("Approve Rate", "96.8%", "24,892 tx")
    col3.metric("MFA Challenge", "2.1%", "540 tx")
    col4.metric("Blocked Fraud", "1.1%", "284 tx")
    col5.metric("Latency (p95)", "58.4 ms", "SLA: <=100ms")

    st.divider()

    # Filter Controls
    f_col1, f_col2, f_col3 = st.columns([2, 2, 4])
    verdict_filter = f_col1.selectbox("Filter by Verdict", ["ALL", "APPROVE", "CHALLENGE_MFA", "BLOCK"])
    min_score = f_col2.slider("Min Risk Score", 0.0, 1.0, 0.0, 0.05)
    search_payer = f_col3.text_input("Search Payer Hash (Salted SHA-256)", "")

    # Mock Real-time Feed
    mock_data = [
        {"Time": "22:34:10", "Tx ID": "9b1deb4d-3b7d", "Amount": "$ 145.50", "Distance": "0.4 km", "Entropy": "3.82", "Score": 0.052, "Verdict": "APPROVE"},
        {"Time": "22:34:08", "Tx ID": "e82491b2-104a", "Amount": "$ 890.00", "Distance": "48.2 km", "Entropy": "4.12", "Score": 0.492, "Verdict": "CHALLENGE_MFA"},
        {"Time": "22:34:04", "Tx ID": "1048ba92-f810", "Amount": "$ 1,420.00", "Distance": "620.5 km", "Entropy": "6.84", "Score": 0.941, "Verdict": "BLOCK"},
        {"Time": "22:34:01", "Tx ID": "a9401928-8921", "Amount": "$ 24.00", "Distance": "1.2 km", "Entropy": "3.40", "Score": 0.018, "Verdict": "APPROVE"},
        {"Time": "22:33:58", "Tx ID": "f8102948-4819", "Amount": "$ 65.00", "Distance": "0.8 km", "Entropy": "3.65", "Score": 0.041, "Verdict": "APPROVE"}
    ]

    df = pd.DataFrame(mock_data)
    if verdict_filter != "ALL":
        df = df[df["Verdict"] == verdict_filter]
    df = df[df["Score"] >= min_score]

    st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# View 2: Transaction Detail & XAI Inspector
# ---------------------------------------------------------
elif navigation == "2. Transaction Detail & XAI":
    st.title("🔍 Transaction Detail & XAI Inspector")
    st.caption("Deep investigative drilldown with dynamic SHAP feature attributions.")

    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        st.markdown("#### Transaction Metadata")
        st.markdown("**Tx Reference:** `1048ba92-f810-4820-9182`")
        st.markdown("**Timestamp:** `1731102000000`")
        st.markdown("**Amount:** `$ 1,420.00` *(+4.8 σ deviation)*")
        st.markdown("**Merchant MCC:** `5411 (Grocery/Retail)`")
        st.markdown("**QR Type:** `0 (Static QR Spoof Risk)`")
        st.markdown("**Scan Latency:** `420 ms (Rapid Bot)`")

    with t_col2:
        st.markdown("#### Spatial Haversine Separation")
        st.metric("Geo-Displacement", "620.5 km", "Critical Drift")
        st.caption("Payer GPS: `(23.810, 90.412)` • Merchant POS: `(22.356, 91.783)`")
        st.info("⚠️ Remote Spoofing Alert: Payer coordinates exceed physical transit bounds.")

    with t_col3:
        st.markdown("#### Dual-Model Risk Breakdown")
        st.metric("Composite Risk Score", "0.931 / 1.000", "Tier: BLOCK")
        st.caption("LightGBM Probability: **0.94** | Isolation Forest: **0.91**")
        st.markdown("<span class='pill-block'>● CRITICAL BLOCK mid-flight</span>", unsafe_allow_html=True)
        st.caption("Ledger Block: `#14820 (Hash: 9f83acb1...)`")

    st.divider()
    st.markdown("### 📊 SHAP TreeExplainer: Feature Contributions")
    st.caption("Polynomial-time Shapley values explaining deviation from base value E[f(x)] = 0.0082:")

    shap_df = pd.DataFrame({
        "Feature": ["haversine_distance_km", "qr_payload_entropy", "amount_zscore", "scan_to_pay_latency_ms", "device_trust_score"],
        "Value": ["620.5 km", "6.84 bits", "+4.80 σ", "420 ms", "0.20"],
        "SHAP Attribution": [+0.42, +0.28, +0.14, +0.08, -0.02],
        "Impact": ["INCREASES_RISK", "INCREASES_RISK", "INCREASES_RISK", "INCREASES_RISK", "REDUCES_RISK"]
    })
    st.bar_chart(shap_df.set_index("Feature")["SHAP Attribution"])

    st.markdown("**Standardized Regulatory Reason Codes:**")
    st.success("1. `GEO_DISTANCE_CRITICAL`: Payer device is 620.5 km from physical terminal.")
    st.warning("2. `PAYLOAD_ENTROPY_ELEVATED`: QR string contains high entropy (6.84 bits).")
    st.error("3. `AMOUNT_DEVIATION_EXTREME`: Amount ($1,420.00) deviates by +4.8 σ from customer mean.")

# ---------------------------------------------------------
# View 3: Fraud Vector Simulator
# ---------------------------------------------------------
elif navigation == "3. Fraud Vector Simulator":
    st.title("🧪 Interactive Fraud Vector Simulator")
    st.caption("Simulate real-time attacks and test hybrid model defense responsiveness.")

    preset = st.selectbox(
        "Attack Scenario Preset",
        [
            "1. Normal Routine Payment",
            "2. Physical Sticker Replacement (Quishing)",
            "3. Dynamic MITM Amount Tampering",
            "4. High-Velocity Micro-Probing Bot"
        ]
    )

    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.markdown("#### Input Parameters")
        if "Quishing" in preset:
            default_dist, default_entropy, default_amt, default_lat = 450.0, 6.54, 420.0, 800
        elif "MITM" in preset:
            default_dist, default_entropy, default_amt, default_lat = 1.2, 4.10, 2800.0, 3500
        elif "Micro-Probing" in preset:
            default_dist, default_entropy, default_amt, default_lat = 0.8, 3.80, 5.0, 250
        else:
            default_dist, default_entropy, default_amt, default_lat = 0.5, 3.60, 45.0, 4200

        sim_amount = st.slider("Transaction Amount ($)", 1.0, 5000.0, float(default_amt))
        sim_dist = st.slider("Haversine Distance (km)", 0.1, 800.0, float(default_dist))
        sim_latency = st.slider("Scan-to-Pay Latency (ms)", 100, 30000, int(default_lat))
        sim_entropy = st.slider("QR Payload Entropy (bits/char)", 1.0, 8.0, float(default_entropy))

        run_btn = st.button("⚡ Simulate Payment Transaction", type="primary", use_container_width=True)

    with s_col2:
        st.markdown("#### Real-Time Authorization Output")
        if run_btn:
            with st.spinner("Processing in sub-100ms pipeline..."):
                time.sleep(0.04)  # Simulate 40ms execution
                if sim_dist > 200 or sim_entropy > 5.5 or sim_amount > 2000:
                    st.error("🛑 VERDICT: BLOCK (High Fraud Threat Intercepted)")
                    score = 0.942
                elif sim_dist > 30 or sim_amount > 500:
                    st.warning("🛡️ VERDICT: CHALLENGE_MFA (Step-Up Required)")
                    score = 0.495
                else:
                    st.success("✓ VERDICT: APPROVE (Payment Authorized)")
                    score = 0.048

                st.metric("Composite Risk Score", f"{score:.4f}", f"Latency: 38.4 ms (SLA <= 100ms)")
                st.caption(f"SHA-256 Ledger Block Hash: `{hashlib.sha256(str(score).encode()).hexdigest()}`")
        else:
            st.info("Adjust parameters on the left and click **Simulate Payment Transaction**.")

# ---------------------------------------------------------
# View 4: Benchmark Scoreboard
# ---------------------------------------------------------
elif navigation == "4. Benchmark Scoreboard":
    st.title("🏆 Model Performance Scoreboard")
    st.caption("Empirical evaluation metrics and algorithm comparison on holdout test partition.")

    bench_df = pd.DataFrame([
        {"Model": "LightGBM (Production)", "Recall": "98.2%", "Precision": "92.8%", "F2-Score": "0.970", "PR-AUC": "0.915", "p95 Latency": "32 ms", "Memory": "45 MB"},
        {"Model": "Random Forest", "Recall": "94.5%", "Precision": "91.2%", "F2-Score": "0.938", "PR-AUC": "0.892", "p95 Latency": "48 ms", "Memory": "85 MB"},
        {"Model": "PyTorch Deep MLP", "Recall": "92.1%", "Precision": "89.5%", "F2-Score": "0.915", "PR-AUC": "0.870", "p95 Latency": "62 ms", "Memory": "40 MB"},
        {"Model": "Support Vector Machine", "Recall": "88.4%", "Precision": "86.1%", "F2-Score": "0.879", "PR-AUC": "0.835", "p95 Latency": "85 ms", "Memory": "70 MB"},
        {"Model": "Isolation Forest (Anomaly)", "Recall": "89.0%", "Precision": "84.2%", "F2-Score": "0.880", "PR-AUC": "0.820", "p95 Latency": "18 ms", "Memory": "38 MB"}
    ])
    st.dataframe(bench_df, use_container_width=True, hide_index=True)

    st.markdown("### 💰 Asymmetric Financial Loss Utility")
    st.caption("Total Loss = C_fraud * FN + C_friction * FP + C_review * Challenges")
    c1, c2, c3 = st.columns(3)
    c1.metric("Financial Loss (LightGBM)", "$ 1,240.00", "-84% vs Legacy Rules")
    c2.metric("Financial Loss (Legacy Rules)", "$ 7,850.00", "Baseline")
    c3.metric("Net Economic Savings", "$ 6,610.00", "High Commercial Value")

# ---------------------------------------------------------
# View 5: Ledger & Audit Explorer
# ---------------------------------------------------------
elif navigation == "5. Ledger & Audit Explorer":
    st.title("🛡️ Cryptographic Ledger Explorer")
    st.caption("Sequential SHA-256 parent block hash chaining for non-repudiation.")

    st.success("✅ SYSTEM INTEGRITY: VERIFIED (14,820 / 14,820 Blocks Intact)")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Run Cryptographic Chain Audit", type="primary", use_container_width=True):
            st.balloons()
            st.success("Chain Scan Complete: 100% digest matches across 14,820 blocks (0.12s scan).")
    with b2:
        st.button("Export Cryptographic Audit Package (JSONL)", use_container_width=True)

    st.markdown("#### Recent Block Sequence")
    ledger_mock = pd.DataFrame([
        {"Block #": 14820, "Prev Hash": "8f92a104b820...", "Block Hash": "9f83acb18204...", "Verdict": "BLOCK", "Time": "22:34:04"},
        {"Block #": 14819, "Prev Hash": "3c8102948102...", "Block Hash": "8f92a104b820...", "Verdict": "CHALLENGE_MFA", "Time": "22:34:08"},
        {"Block #": 14818, "Prev Hash": "110492810482...", "Block Hash": "3c8102948102...", "Verdict": "APPROVE", "Time": "22:34:10"},
        {"Block #": 14817, "Prev Hash": "774819204812...", "Block Hash": "110492810482...", "Verdict": "APPROVE", "Time": "22:33:58"}
    ])
    st.dataframe(ledger_mock, use_container_width=True, hide_index=True)

