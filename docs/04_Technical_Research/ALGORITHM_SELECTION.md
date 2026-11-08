# Mathematical Formulation & Algorithm Selection

**Project:** Advanced Quick Response (QR) Code Payment Fraud Detection System  
**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 04)  
**Parent Document:** `docs/04_Technical_Research/TECHNOLOGY_COMPARISON.md`  
**Reference Document:** `source/PROJECT_SPEC.md` | `research/REFERENCES.md`

---

## 1. Supervised Production Engine: LightGBM

### 1.1 Mathematical Formulation & Tree Splitting
LightGBM constructs an ensemble of $K$ decision trees via gradient-boosted decision trees (GBDT). The objective function at iteration $t$ is:
$$\mathcal{L}^{(t)} = \sum_{i=1}^N l\left(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)\right) + \Omega(f_t)$$
where $l$ is the binary cross-entropy loss and $\Omega(f_t) = \gamma T + \frac{1}{2}\lambda \sum_{j=1}^T w_j^2$ regularizes tree complexity.

LightGBM accelerates split finding using two core algorithmic innovations:
1. **Gradient-Based One-Side Sampling (GOSS):** Retains all instances with large gradients ($g_i = \partial \mathcal{L} / \partial \hat{y}_i$) and randomly samples a fraction $b$ of instances with small gradients, re-weighting them by $\frac{1-a}{b}$ to preserve the training data distribution.
2. **Exclusive Feature Bundling (EFB):** Bins mutually exclusive sparse features into dense composite feature bins, drastically reducing histogram construction time from $O(\text{data} \times \text{features})$ to $O(\text{data} \times \text{bundles})$.

### 1.2 Justification for QR Fraud Detection
- **Leaf-Wise Tree Growth:** Expands the leaf with maximum loss reduction, capturing complex non-linear combinations of spatial distance and transaction velocity faster than depth-wise algorithms.
- **Sub-10ms Inference:** Generates predictions in $3 - 8\text{ ms}$ on single-instance vectors.
- **Native Imbalance Handling:** Supports `is_unbalance=True` and `scale_pos_weight`, ensuring minority fraud patterns receive proportional gradient updates.

---

## 2. Unsupervised Anomaly Engine: Isolation Forest

### 2.1 Mathematical Formulation & Path Length Metric
Isolation Forest isolates anomalies by exploiting the property that anomalous instances require fewer recursive partitions to isolate in a feature space than normal instances.

Given a dataset $X = \{x_1, \dots, x_n\}$, an Isolation Tree (iTree) recursively splits data by randomly selecting a feature $q$ and a split value $p \in [\min(x_{\cdot, q}), \max(x_{\cdot, q})]$ until either:
1. The tree reaches a maximum height limit: $h_{\max} = \lceil\log_2 n\rceil$.
2. The terminal node contains $|X| \le 1$ instance.

Let $h(x)$ represent the path length (number of edges traversed from root to external node) for instance $x$ in an iTree. The average path length of unsuccessful searches in a Binary Search Tree (BST) of size $n$ is:
$$c(n) = 2 \ln(n - 1) + 0.5772156649 \text{ (Euler-Mascheroni Constant)} - \frac{2(n - 1)}{n}$$

The normalized anomaly score $s(x, n)$ across an ensemble of $m$ iTrees is defined as:
$$s(x, n) = 2^{-\frac{\mathbb{E}[h(x)]}{c(n)}}$$
- If $\mathbb{E}[h(x)] \to 0 \implies s \to 1$: Instance $x$ is highly anomalous.
- If $\mathbb{E}[h(x)] \to c(n) \implies s \to 0.5$: Instance $x$ exhibits typical, average behavior.
- If $\mathbb{E}[h(x)] \to n - 1 \implies s \to 0$: Instance $x$ is completely normal.

### 2.2 Justification for QR Fraud Detection
- **Unsupervised Cold-Start:** Trained strictly on known legitimate transaction streams; requires no labeled fraud instances.
- **Zero-Day Catch:** Flags novel exploit vectors (e.g., unexpected combinations of extreme device trust and zero latency) that have never appeared in training sets.

---

## 3. Hybrid Risk Scoring & Arbitration Formulation

The composite risk score $S_{\text{composite}}$ is computed through calibrated linear fusion accompanied by non-linear escalation gating:

$$S_{\text{composite}} = w_1 \cdot P_{\text{supervised}}(\text{Fraud} \mid X) + w_2 \cdot S_{\text{anomaly}}(X)$$
where default baseline weights are:
$$w_1 = 0.70, \quad w_2 = 0.30 \quad (w_1 + w_2 = 1.0)$$

### Three-Tier Decision Boundary & Escalation Logic:
$$\text{Verdict}(X) = \begin{cases}
\mathbf{APPROVE}, & \text{if } S_{\text{composite}} < 0.30 \text{ and } S_{\text{anomaly}} \le 0.80 \\
\mathbf{CHALLENGE\_MFA}, & \text{if } 0.30 \le S_{\text{composite}} \le 0.70 \\
\mathbf{CHALLENGE\_MFA}, & \text{if } P_{\text{supervised}} \in [0.25, 0.45] \text{ and } S_{\text{anomaly}} > 0.80 \text{ (Zero-Day Escalation)} \\
\mathbf{BLOCK}, & \text{if } S_{\text{composite}} > 0.70
\end{cases}$$

---

## 4. Class Imbalance Mitigation: Borderline-SMOTE

### 4.1 Borderline Partitioning
Given the minority class set $P$ (fraud) and majority class set $N$ (legitimate):
For each minority instance $p_i \in P$, determine its $m$ nearest neighbors from the entire training set $P \cup N$. Let $m'$ denote the number of majority neighbors among the $m$ nearest neighbors:
- If $m' = m$: $p_i$ is treated as noise and excluded from oversampling.
- If $0 \le m' < \frac{m}{2}$: $p_i$ is safe and well inside minority space; no synthesis needed.
- If $\frac{m}{2} \le m' < m$: $p_i$ belongs to the **$DANGER$** set (near the borderline).

### 4.2 Synthetic Point Generation
For each instance $p_i \in DANGER$, randomly choose $s$ neighbors from its $k$-nearest minority neighbors ($p_i \in P$). Generate synthetic instances:
$$x_{\text{new}} = p_i + \lambda \cdot (p_{ij} - p_i), \quad \lambda \sim \text{Uniform}(0, 1), \quad j = 1, \dots, s$$

### 4.3 Justification
Unlike standard SMOTE which interpolates indiscriminately across all minority points (risking blending with deep majority points), Borderline-SMOTE concentrates exclusively on resolving the ambiguous boundary where false negatives occur.

---

## 5. Explainable AI: SHAP TreeExplainer

### 5.1 Game-Theoretic Shapley Values
For an individual prediction $f(x)$, the local explanation model $g(z')$ is an additive feature attribution:
$$f(x) = g(z') = \phi_0 + \sum_{j=1}^M \phi_j z_j'$$
where $\phi_0 = \mathbb{E}[f(x)]$ is the base value, and $\phi_j \in \mathbb{R}$ is the Shapley value for feature $j$:
$$\phi_j = \sum_{S \subseteq F \setminus \{j\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f(S \cup \{j\}) - f(S) \right]$$

### 5.2 TreeExplainer Computational Optimization
While model-agnostic KernelSHAP has exponential complexity $O(2^{|F|})$, **TreeExplainer** recursively evaluates subtree expectations in polynomial time:
$$O(T \cdot L \cdot D^2)$$
where $T$ is the number of trees ($100$), $L$ is the maximum number of leaves ($31$), and $D$ is the maximum tree depth ($6$).
- Execution time on a single transaction feature vector: **$\approx 15 - 28\text{ ms}$**.

---

## 6. Cryptographic Audit Chaining: SHA-256 Ledger

Each transaction authorization verdict is permanently bound to a block digest:
$$H_k = \text{SHA256}\left(H_{k-1} \,\|\, \text{TxID}_k \,\|\, S_{\text{composite}} \,\|\, \text{Verdict}_k \,\|\, t_k \,\|\, \text{SaltedPayerHash}\right)$$
- **Genesis Block ($H_0$):** Fixed initial constant seed.
- **Verification Complexity:** Linear scan $O(N)$ verifying $H_k \stackrel{?}{=} \text{SHA256}(H_{k-1} \,\|\, \dots)$.
- Any unauthorized update to historical fields alters $H_k$, instantly breaking the chain at block $k$.

---

## 7. Privacy-Preserving Federated Learning: FedAvg

Simulates $K=3$ decentralized banking nodes collaborating without sharing raw customer records:
1. **Local Model Training:** Each client $k \in \{1, \dots, K\}$ executes $E$ local epochs using SGD:
   $$w_{t+1}^k \leftarrow w_t - \eta \nabla F_k(w_t)$$
2. **Global Server Aggregation:** The central coordinator collects parameter weights and computes the weighted average:
   $$W_{t+1} = \sum_{k=1}^K \frac{n_k}{n} w_{t+1}^k$$
   where $n_k$ is the number of local samples at node $k$, and $n = \sum n_k$.

