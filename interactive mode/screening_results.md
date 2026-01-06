# Screening Results

**Topic:** EEG noise removal transformer
**Session ID:** 31812731-73d9-4e57-8015-b892ec7cd9a3
**Date:** 2026-01-06

## Screening Criteria

### Inclusion Criteria
- Directly addresses EEG signal processing
- Studies transformer/deep learning for artifact/noise removal
- Reports denoising/artifact removal outcomes
- Published 2015+
- Peer-reviewed

### Exclusion Criteria
- Non-EEG focused (e.g., EMG only, heart sounds, birdsong)
- General review without EEG noise/denoising focus
- Unrelated ML/AI applications (cancer, organoids, etc.)
- No methodological contribution to EEG denoising

### Scoring Weights
| Criterion | Weight |
|-----------|--------|
| Relevance to topic | 40% |
| Methodological quality | 30% |
| Evidence strength | 20% |
| Unique contribution | 10% |

---

## Summary
- **Total papers screened:** 38
- **Included:** 14
- **Excluded:** 24
- **Threshold:** 3.5

---

## Included Papers (Score ≥ 3.5)

| ID | Title | Year | Score | Rationale |
|----|-------|------|-------|-----------|
| P1 | ART: Artifact Removal Transformer for Reconstructing Noise-Free Multichannel EEG | 2024 | 5.0 | **Core paper.** Directly addresses transformer-based EEG artifact removal. High relevance, novel architecture. |
| P3 | CT-DCENet: Deep EEG Denoising via CNN-Transformer-Based Dual-Stage Collaborative | 2025 | 5.0 | **Core paper.** CNN-Transformer hybrid for EEG denoising. State-of-the-art approach. |
| P4 | Augmenting brain-computer interfaces with ART | 2025 | 4.9 | **Core paper.** ART application for BCI. Strong methodology, recent publication. |
| P31 | EEG Artifact Removal using Stacked Multi-Head Attention Transformer Architecture | 2024 | 5.0 | **Core paper.** Multi-head attention transformer specifically for EEG artifacts. |
| P32 | A GAN Guided Parallel CNN and Transformer Network for EEG Denoising | 2025 | 5.0 | **Core paper.** GAN + CNN + Transformer hybrid for EEG denoising. Novel architecture. |
| P33 | EEGDnet: Fusing non-local and local self-similarity for EEG signal denoising with attention | 2022 | 5.0 | **Core paper.** Attention-based EEG denoising with self-similarity. |
| P34 | EEGDfus: A Conditional Diffusion Model for Fine-Grained EEG Denoising | 2025 | 5.0 | **Core paper.** Diffusion model approach for EEG denoising. Cutting-edge method. |
| P35 | DHCT-GAN: Dual-Branch Hybrid CNN-Transformer for EEG Signal Quality | 2025 | 5.0 | **Core paper.** Dual-branch CNN-Transformer GAN architecture for EEG. |
| P10 | Deep Learning in EEG-Based BCIs: Comprehensive Review of Transformer Models | 2023 | 4.4 | **Review paper.** Comprehensive transformer survey for EEG-BCIs. Essential background. |
| P14 | Exploring Convolutional Neural Network Architectures for EEG Feature Extraction | 2024 | 3.9 | **Methodological context.** CNN architectures for EEG. Foundation for hybrid approaches. |
| P8 | A Review of Issues Related to Data Acquisition and Analysis in EEG/MEG Studies | 2017 | 3.9 | **Foundational review.** EEG noise sources and preprocessing challenges. |
| P9 | Motor Imagery EEG Signals Classification Based on Mode Amplitude and Frequency | 2019 | 3.5 | **Application context.** EEG preprocessing for BCI classification. |
| P18 | Role of machine learning and deep learning in EEG-based BCI emotion recognition | 2024 | 3.5 | **Application context.** ML/DL for EEG with preprocessing discussion. |
| P20 | Epileptic Seizures Detection in EEG Signals Using Fusion Handcrafted and Deep Learning | 2021 | 3.5 | **Clinical application.** EEG preprocessing for seizure detection. |

---

## Excluded Papers

| ID | Title | Score | Reason |
|----|-------|-------|--------|
| P2 | Feature dimensionality reduction: a review | 2.8 | General ML review, not EEG-specific |
| P5 | A Review of Wavelet Analysis and Its Applications | 2.8 | Wavelet theory, not EEG transformer focus |
| P6 | Early Disease Detection Using AI: Cancer | 2.0 | Wrong domain (cancer diagnosis) |
| P7 | Shared computational principles for language processing | 2.8 | NLP focus, not EEG denoising |
| P11 | Window Functions and Signal Processing | 2.8 | Signal processing theory, not EEG |
| P12 | Portable Drowsiness Detection EEG | 3.4 | EEG application but not denoising focus |
| P13 | Comprehensive literature review of AI techniques | 2.5 | Too general, no abstract |
| P15 | SQUIDs in biomagnetism | 2.0 | MEG hardware focus, not denoising |
| P16 | Shaping high-performance wearable robots | 2.0 | Robotics, not EEG denoising |
| P17 | Emotion Recognition Using Different Sensors | 2.5 | Multi-sensor emotion, not EEG denoising |
| P19 | Remote monitoring cardiorespiratory UAV | 2.0 | Wrong domain (UAV, heart rate) |
| P21 | Organoid intelligence (OI) | 2.3 | Wrong domain (organoids) |
| P22 | AI and Neuroscience: Transformative Synergies | 2.8 | General AI review, not denoising |
| P23 | Effects of Age on Cortical Tracking of Speech | 3.0 | Speech perception, not denoising |
| P24 | Parkinson's Disease EMG Data Augmentation DCGANs | 3.0 | EMG not EEG, different modality |
| P25 | Real-time decoding speech dialogue cortical activity | 3.3 | Speech decoding, not artifact removal |
| P26 | End-to-End Deep Learning Denoising Heart Sounds | 3.0 | Heart sounds, not EEG |
| P27 | Soft Electronics Health Monitoring ML | 2.8 | Wearables general, not EEG denoising |
| P28 | Cross-Subject Zero Calibration Drowsiness EEG | 3.4 | Drowsiness classification, not denoising |
| P29 | Birdsong Denoising Using Wavelets | 2.0 | Wrong domain (birdsong) |
| P30 | Multi-Objective Feature Selection Review | 2.8 | Feature selection, not denoising |
| P36 | Federated deep learning epilepsy seizure detection | 3.4 | Seizure detection, not denoising methodology |
| P37 | Adaptive Prototype Transformers Neonatal Seizures | 3.4 | Seizure detection, not noise removal |
| P38 | GLEAM multimodal lower back pain detection | 2.0 | Wrong domain (back pain) |

---

## Paper Categories

### Core EEG Transformer Denoising (8 papers)
P1, P3, P4, P31, P32, P33, P34, P35

### Review/Survey Papers (2 papers)
P8, P10

### Application Context (4 papers)
P9, P14, P18, P20
