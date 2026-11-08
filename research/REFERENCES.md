# Academic References & Research Citations

This document compiles the verified primary research literature cited in the approved thesis proposal. In strict adherence to scientific integrity guidelines, all DOIs, authors, publication years, and venue names have been verified against original publication records.

---

## 1. Verified Literature References

### Ref 1: Systematic Review of ML in Financial Fraud Detection
- **Full Citation:** Ali, A., Abd Razak, S. and Othman, S.H. (2022) 'Financial fraud detection based on machine learning: A systematic literature review', *Applied Sciences*, 12(19), article 9637.
- **DOI:** [10.3390/app12199637](https://doi.org/10.3390/app12199637)
- **Methodology:** Systematic Literature Review (SLR) adhering to Kitchenham methodology analyzing 93 high-quality articles (2010–2021) from IEEE Xplore, ACM DL, ScienceDirect, Scopus, and Web of Science.
- **Key Findings Utilized in This Project:**
  - Identifies prevailing ML algorithms in financial fraud: Logistic Regression, Decision Trees, Random Forest, SVM, ANN, and ensemble techniques.
  - Highlights critical research gaps: acute dataset imbalance, concept drift, high-dimensional feature spaces, and sub-second real-time latency bottlenecks.
  - Motivates our dual-model hybrid architecture (supervised + unsupervised anomaly detection).

### Ref 2: Online Payment Fraud Detection with Imbalanced Data
- **Full Citation:** Almazroi, A.A. and Ayub, N. (2023) 'Online payment fraud detection model using machine learning techniques', *IEEE Access*, 11, pp. 137188–137203.
- **DOI:** [10.1109/ACCESS.2023.3339343](https://doi.org/10.1109/ACCESS.2023.3339343)
- **Key Findings Utilized in This Project:**
  - Evaluates conventional classifiers (Logistic Regression, Decision Trees, Random Forest, KNN, SVM) on heavily skewed transaction datasets.
  - Demonstrates that handcrafted manual features degrade as attack topologies evolve.
  - Proves that standard classifiers suffer from structural majority-class bias unless compensated by oversampling (SMOTE) or algorithmic cost weighting.
  - Directly justifies our adoption of SMOTE and Borderline-SMOTE in `backend/data/preprocessor.py`.

### Ref 3: QR Codes for Payment Card Fraud Detection
- **Full Citation:** Chelouah, R. and Nwaekwu, P. (2026) 'Using QR codes for payment card fraud detection', *Information*, 17(1), p. 39.
- **DOI:** [10.3390/info17010039](https://doi.org/10.3390/info17010039)
- **Key Findings Utilized in This Project:**
  - Investigates emerging QR payment infrastructures, specifically comparing static vs. transaction-specific dynamic QR code threat vectors.
  - Identifies physical sticker spoofing ("quishing"), dynamic payload interception (MITM), and merchant account replacement as primary failure points.
  - Establishes the necessity for specialized feature engineering capturing QR payload entropy, scan-to-pay latencies, and spatial-temporal verification.
  - Directly informs our 16-attribute schema and the `data.feature_engineering` module.

### Ref 4: Comparative Machine Learning Benchmark in Online Payment Fraud
- **Full Citation:** Farouk, M., Shaker, N., AbdElminaam, D. and Elrashidy, O. (2024) 'Fraud_Detection_ML: Machine learning based on online payment fraud detection', *Journal of Computing and Communication*, 3(1), pp. 116–131.
- **DOI:** [10.21608/jocc.2024.339929](https://doi.org/10.21608/jocc.2024.339929)
- **Key Findings Utilized in This Project:**
  - Comparative empirical benchmarking of Decision Trees, Random Forest, AdaBoost, Naive Bayes, Bagging, and LightGBM across online payment datasets.
  - Reports that LightGBM achieves superior recall ($\approx 99\%$) and dramatically lower training/inference times compared to standard tree ensembles and neural networks.
  - Concludes that no single classifier universally dominates across all metrics, justifying an ensemble / benchmark suite.
  - Directly justifies selecting LightGBM as our primary production supervised engine.

### Ref 5: AI & Machine Learning in Digital Payment Technologies
- **Full Citation:** Wang, J. (2022) 'Fraud detection in digital payment technologies using machine learning', *Journal of Economic Theory and Business Management*, 1(2).
- **Key Findings Utilized in This Project:**
  - Explores the rapid evolution of fraud tactics in mobile e-wallets, contactless payments, and instant settlement systems.
  - Demonstrates the total obsolescence of static, hardcoded rule engines against adaptive fraud tactics.
  - Argues for real-time computational inference capable of blocking fraudulent transactions mid-flight rather than post-settlement audits.
  - Underpins our requirement for sub-100ms API response latency and automated multi-tier decision gating.

---

## 2. Theoretical & Methodological Foundations

1. **Synthetic Minority Over-sampling Technique (SMOTE):**
   - Chawla, N.V., Bowyer, K.W., Hall, L.O. and Kegelmeyer, W.P. (2002) 'SMOTE: Synthetic Minority Over-sampling Technique', *Journal of Artificial Intelligence Research*, 16, pp. 321–357.
2. **Isolation Forest (iForest):**
   - Liu, F.T., Ting, K.M. and Zhou, Z.H. (2008) 'Isolation Forest', *2008 Eighth IEEE International Conference on Data Mining*, pp. 413–422.
3. **Consistent Feature Attribution via SHAP:**
   - Lundberg, S.M. and Lee, S.I. (2017) 'A unified approach to interpreting model predictions', *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30.
4. **Federated Learning (FedAvg):**
   - McMahan, B., Moore, E., Ramage, D., Hampson, S. and y Arcas, B.A. (2017) 'Communication-efficient learning of deep networks from decentralized data', *Artificial Intelligence and Statistics (AISTATS)*, PMLR, pp. 1273–1282.

