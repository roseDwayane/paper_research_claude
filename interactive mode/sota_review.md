# State-of-the-Art Review: EEG Noise Removal Using Transformer Architectures

**Date:** 2026-01-06
**Papers Reviewed:** 14
**Time Span:** 2017-2025

---

## Executive Summary

Electroencephalography (EEG) signal denoising is a critical preprocessing step that directly impacts the reliability of neuroscientific analysis and brain-computer interface (BCI) performance. Traditional approaches such as Independent Component Analysis (ICA), wavelet transforms, and adaptive filtering have been the mainstay for decades but require manual intervention and struggle with complex, mixed artifacts (Puce & Hämäläinen, 2017).

The emergence of deep learning, particularly transformer architectures originally designed for natural language processing, has catalyzed a paradigm shift in EEG denoising methodology. Since 2022, transformer-based approaches have demonstrated superior performance in capturing both local and global temporal dependencies in EEG signals, outperforming conventional convolutional neural networks (CNNs) and recurrent neural networks (RNNs) in artifact removal tasks (Abibullaev et al., 2023; Pu et al., 2022).

This review synthesizes 14 papers spanning 2017-2025, identifying five major themes: (1) pure transformer architectures, (2) CNN-transformer hybrid models, (3) GAN-guided denoising frameworks, (4) attention mechanisms and self-similarity, and (5) clinical applications and BCI integration. The field has rapidly evolved from foundational attention-based methods (EEGDnet, 2022) to sophisticated dual-branch architectures combining diffusion models with transformers (EEGDfus, 2025), achieving correlation coefficients exceeding 0.98 for artifact removal.

---

## Theme 1: Pure Transformer Architectures for EEG Denoising

### Current State of Knowledge

Pure transformer architectures represent the most direct application of attention mechanisms to EEG artifact removal. The Artifact Removal Transformer (ART) introduced by Chuang et al. (2024, 2025) is the seminal work in this domain, employing transformer architecture to capture transient millisecond-scale dynamics characteristic of EEG signals.

### Key Findings

1. **End-to-end multichannel denoising**: ART provides a holistic solution that simultaneously addresses multiple artifact types (EOG, EMG, ECG) in multichannel EEG data without requiring artifact-specific preprocessing (P1, P4).

2. **ICA-enhanced training data generation**: The use of Independent Component Analysis to generate noisy-clean EEG pairs fortifies supervised learning scenarios, addressing the chronic shortage of labeled training data (P1, P4).

3. **Stacked multi-head attention**: Multiple attention layers effectively capture long-range temporal dependencies that previous deep learning models failed to address (P31).

4. **Superior benchmark performance**: ART surpasses other deep-learning-based artifact removal methods on EEGdenoiseNet dataset, setting new benchmarks in MSE and SNR metrics (P1, P31).

### Methodological Approaches

- **Architecture**: Multi-head self-attention layers with positional encoding for temporal sequence modeling
- **Training**: Supervised learning with synthetic noisy-clean pairs
- **Evaluation**: MSE, SNR, correlation coefficient, source localization accuracy, component classification

### Limitations in Current Literature

- Computational complexity not explicitly addressed; real-time applicability uncertain
- Limited validation on clinical-grade recordings from actual patient populations
- Heavy reliance on semi-simulated datasets (EEGdenoiseNet)
- P1 and P4 represent the same method from the same research group, limiting independent validation

---

## Theme 2: CNN-Transformer Hybrid Models

### Current State of Knowledge

Recognizing that CNNs excel at capturing local patterns while transformers capture global dependencies, researchers have developed hybrid architectures that leverage both strengths. This has become the dominant paradigm in 2024-2025 publications.

### Key Findings

1. **Dual-stage collaborative learning**: CT-DCENet employs a dual-stage training framework where morphological characteristics and detailed characteristics are learned successively, achieving 0.79 dB SNR improvement and 1.9% RRMSE reduction over state-of-the-art for mixed artifacts (P3).

2. **Parallel processing of local and global features**: GCTNet uses parallel CNN blocks and transformer blocks to simultaneously capture local and global temporal dependencies, achieving 11.15% RRMSE reduction and 9.81% SNR improvement for EMG artifacts (P32).

3. **Multi-scale feature extraction**: EEGDfus combines CNN and Transformer in a dual-branch structure for multi-scale feature extraction, achieving correlation coefficients of 0.983 and 0.992 on EEGdenoiseNet and SSED datasets respectively (P34).

4. **Complementary strength integration**: The combination addresses the limitation of pure transformers (high computational cost, need for large data) while maintaining their global context modeling capability (P3, P32, P34, P35).

### Methodological Approaches

- **Architecture**: Parallel or sequential CNN-Transformer branches with feature fusion mechanisms
- **Training**: End-to-end supervised learning, often with ensemble or collaborative strategies
- **Datasets**: EEGdenoiseNet (primary), SSED, custom semi-simulated data
- **Metrics**: RRMSE, SNR, correlation coefficient (CC), PSD analysis

### Limitations in Current Literature

- Increased model complexity may limit clinical deployment
- Training stability with multiple branches requires careful hyperparameter tuning
- Cross-dataset generalization not thoroughly evaluated

---

## Theme 3: GAN-Guided Denoising Frameworks

### Current State of Knowledge

Generative Adversarial Networks (GANs) have been integrated with transformer-based denoising to address the limitation of point-wise loss functions, which often result in over-smoothed outputs. The discriminator provides holistic signal consistency enforcement.

### Key Findings

1. **Holistic consistency enforcement**: GCTNet employs a discriminator to detect and correct holistic inconsistencies between clean and denoised EEG signals, moving beyond point-wise reconstruction losses (P32).

2. **Dual-branch artifact learning**: DHCT-GAN independently learns features from both clean EEG signals and artifact signals, then fuses information through adaptive gating networks. This cross-disciplinary insight improves denoising by explicitly modeling artifact characteristics (P35).

3. **Adaptive gating mechanisms**: Learned gating networks dynamically balance contributions from different branches based on signal characteristics (P35).

4. **PSD preservation**: GAN-based methods show superior power spectral density preservation compared to pure reconstruction approaches (P35).

### Methodological Approaches

- **Architecture**: Generator (CNN-Transformer hybrid) + Discriminator (signal authenticity critic)
- **Training**: Adversarial training with reconstruction loss + adversarial loss
- **Innovation**: Artifact-aware dual-branch learning
- **Evaluation**: Waveform analysis, PSD analysis, multiple quantitative metrics

### Limitations in Current Literature

- GAN training instability may affect reproducibility
- Mode collapse risks in artifact-heavy segments
- Computational overhead from discriminator training

---

## Theme 4: Attention Mechanisms and Self-Similarity Exploitation

### Current State of Knowledge

Self-attention mechanisms enable models to capture both non-local (global) and local self-similarity patterns in EEG signals. This theme represents the theoretical foundation underlying transformer effectiveness for EEG denoising.

### Key Findings

1. **Non-local and local self-similarity fusion**: EEGDnet (2022) pioneered fusing non-local self-similarity in self-attention blocks with local self-similarity in feed-forward blocks, achieving 18% and 11% improvements in correlation coefficients for ocular and muscle artifact removal respectively (P33).

2. **2D transformer for 1D signals**: Novel encoding strategies convert 1D EEG signals to 2D representations for transformer processing, enabling spatial relationship modeling (P33).

3. **Comprehensive transformer application review**: Transformers have been successfully applied across multiple BCI domains including motor imagery decoding, emotion recognition, sleep stage analysis, and speech reconstruction (P10).

4. **Temporal dependency modeling**: Self-attention effectively captures transient millisecond-scale dynamics characteristic of EEG, which is critical for preserving signal fidelity (P1, P10).

### Methodological Approaches

- **Attention types**: Multi-head self-attention, cross-attention, spatial attention
- **Positional encoding**: Learned or sinusoidal position embeddings for sequence ordering
- **Feature fusion**: Concatenation, addition, or gated fusion of attention outputs

### Limitations in Current Literature

- Interpretability of attention weights for EEG signals not well explored
- Computational cost scales quadratically with sequence length
- Optimal attention head configuration remains empirically determined

---

## Theme 5: Clinical Applications and BCI Integration

### Current State of Knowledge

The ultimate goal of EEG denoising is to improve downstream task performance in clinical and BCI applications. Several studies provide context for how denoising impacts real-world applications.

### Key Findings

1. **BCI performance enhancement**: ART demonstrates that improved artifact removal directly translates to better BCI classification accuracy, particularly in naturalistic environments with high artifact contamination (P4).

2. **Motor imagery classification**: Effective preprocessing is critical for motor imagery EEG classification, with empirical wavelet transform and feature extraction methods achieving 95.2% accuracy (P9).

3. **Emotion recognition**: EEG-based emotion recognition systems require robust denoising as a prerequisite, with deep learning methods showing promise but requiring clean input signals (P18).

4. **Seizure detection**: Epileptic seizure detection in EEG achieves 99.71% accuracy when proper preprocessing and deep learning (CNN-RNN) are combined, demonstrating the clinical value of quality signals (P20).

5. **Data acquisition challenges**: EEG recordings are fundamentally susceptible to multiple artifact sources including physiological (EOG, EMG, ECG), environmental, and equipment-related noise, necessitating robust denoising (P8).

### Methodological Approaches

- **Application domains**: BCI, epilepsy monitoring, emotion recognition, cognitive neuroscience
- **Signal types**: Multi-channel EEG (32-128 channels), single-channel prefrontal EEG
- **Preprocessing pipelines**: Filtering → artifact removal → feature extraction → classification

### Limitations in Current Literature

- Gap between benchmark performance and real-world clinical validation
- Limited studies on online/real-time denoising for BCI
- Cross-subject generalization remains challenging

---

## Cross-Theme Synthesis

### Convergent Findings

1. **Transformer superiority for temporal modeling**: All studies agree that transformer architectures outperform traditional CNNs and RNNs in capturing long-range temporal dependencies in EEG signals (P1, P3, P10, P31, P32, P33).

2. **Hybrid approaches dominate recent literature**: The combination of CNN (local) and Transformer (global) feature extraction has emerged as the dominant paradigm in 2024-2025 publications (P3, P32, P34, P35).

3. **EEGdenoiseNet as standard benchmark**: The semi-simulated EEGdenoiseNet dataset has become the de facto standard for method comparison, enabling reproducible benchmarking (P31, P32, P33, P34).

4. **Multi-artifact handling**: Modern approaches aim to simultaneously address EOG, EMG, and ECG artifacts rather than treating them separately (P1, P3, P4, P32).

5. **Quantitative improvements**: Recent methods consistently achieve correlation coefficients > 0.95 and SNR improvements > 5 dB for standard artifact types.

### Divergent Findings

1. **Architecture complexity vs. efficiency**: Some studies prioritize state-of-the-art performance (P3, P34) while others emphasize practical deployment considerations (P31, P33).

2. **Training data generation**: Approaches vary from ICA-based synthetic generation (P1, P4) to purely semi-simulated mixing (P32, P33) to real-world recording augmentation.

3. **GAN utility**: While P32 and P35 advocate for GAN-guided training, other methods achieve comparable results without adversarial components (P3, P34).

4. **Diffusion vs. direct reconstruction**: P34 introduces diffusion models as a paradigm shift, while other methods use direct signal reconstruction.

### Methodological Patterns

**Strengths:**
- Strong quantitative evaluation with multiple metrics (RRMSE, SNR, CC)
- Comparison against established baselines
- Open benchmark datasets enabling reproducibility

**Weaknesses:**
- Over-reliance on semi-simulated data (EEGdenoiseNet)
- Limited real-world clinical validation
- Computational requirements not systematically reported
- Cross-dataset and cross-subject generalization understudied

---

## Conclusion

The field of transformer-based EEG denoising has undergone rapid evolution from 2022 to 2025. The foundational work of EEGDnet (2022) establishing attention mechanisms for EEG signals has been extended through increasingly sophisticated architectures combining CNNs, transformers, GANs, and diffusion models. Current state-of-the-art methods (CT-DCENet, GCTNet, EEGDfus, DHCT-GAN) achieve excellent benchmark performance with correlation coefficients exceeding 0.98.

However, significant gaps remain between benchmark performance and clinical utility. The field lacks:
1. Validation on clinical-grade, real-world EEG recordings
2. Real-time processing capabilities for online BCI applications
3. Systematic comparison with traditional methods (ICA, wavelet)
4. Lightweight architectures suitable for edge deployment
5. Cross-dataset and cross-subject generalization studies

These gaps present opportunities for future research to bridge the translation gap between algorithmic advances and clinical impact. The convergence of deep learning architectures with domain-specific knowledge about EEG artifacts represents a promising direction for the next generation of denoising methods.

---

## References Summary

| Category | Papers | Key Citations |
|----------|--------|---------------|
| Core Transformer | 8 | Chuang et al. (2024, 2025); Tang et al. (2025); Yin et al. (2025); Pu et al. (2022); Huang et al. (2025); Cai et al. (2025); Gowtham Reddy et al. (2024) |
| Review | 2 | Puce & Hämäläinen (2017); Abibullaev et al. (2023) |
| Context | 4 | Sadiq et al. (2019); Rakhmatulin et al. (2024); Samal & Hashmi (2024); Malekzadeh et al. (2021) |
