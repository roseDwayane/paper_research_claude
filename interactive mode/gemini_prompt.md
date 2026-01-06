# Gemini Prompt: Write Introduction Section

**Copy everything below this line and paste into Google AI Studio or Gemini.**

---

## TASK

You are a scientific writing assistant specializing in biomedical engineering papers. Write the **Introduction section** for a research paper on efficient transformer architectures for real-time EEG denoising.

**Target Journal:** IEEE Journal of Biomedical and Health Informatics (J-BHI)
**Word Count:** 2,500-3,000 words
**Style:** Formal academic, third person, APA 7th edition citations

---

## PAPER MANIFEST (ONLY CITE THESE PAPERS)

You may ONLY cite papers from this manifest. Do NOT invent or hallucinate any citations.

| ID | In-Text Citation | Year | Category | Title |
|----|------------------|------|----------|-------|
| P1 | (Chuang et al., 2024) | 2024 | Core | ART: Artifact Removal Transformer for Reconstructing Noise-Free Multichannel EEG |
| P3 | (Tang et al., 2025) | 2025 | Core | CT-DCENet: Deep EEG Denoising via CNN-Transformer-Based Dual-Stage Collaborative |
| P4 | (Chuang et al., 2025) | 2025 | Core | Augmenting brain-computer interfaces with ART |
| P8 | (Puce & Hämäläinen, 2017) | 2017 | Review | A Review of Issues Related to Data Acquisition and Analysis in EEG/MEG Studies |
| P9 | (Sadiq et al., 2019) | 2019 | Context | Motor Imagery EEG Signals Classification Based on Mode Amplitude and Frequency |
| P10 | (Abibullaev et al., 2023) | 2023 | Review | Deep Learning in EEG-Based BCIs: Comprehensive Review of Transformer Models |
| P14 | (Rakhmatulin et al., 2024) | 2024 | Context | Exploring Convolutional Neural Network Architectures for EEG Feature Extraction |
| P18 | (Samal & Hashmi, 2024) | 2024 | Context | Role of machine learning and deep learning in EEG-based BCI emotion recognition |
| P20 | (Malekzadeh et al., 2021) | 2021 | Context | Epileptic Seizures Detection in EEG Signals Using Fusion Handcrafted and Deep Learning |
| P31 | (Gowtham Reddy et al., 2024) | 2024 | Core | EEG Artifact Removal using Stacked Multi-Head Attention Transformer Architecture |
| P32 | (Yin et al., 2025) | 2025 | Core | A GAN Guided Parallel CNN and Transformer Network for EEG Denoising |
| P33 | (Pu et al., 2022) | 2022 | Core | EEGDnet: Fusing non-local and local self-similarity for EEG signal denoising |
| P34 | (Huang et al., 2025) | 2025 | Core | EEGDfus: A Conditional Diffusion Model for Fine-Grained EEG Denoising |
| P35 | (Cai et al., 2025) | 2025 | Core | DHCT-GAN: Dual-Branch Hybrid CNN-Transformer for EEG Signal Quality |

**Total citable papers: 14**

---

## RESEARCH GAPS TO ADDRESS

### GAP_001: Real-Time Lightweight Architectures (CRITICAL - PRIMARY FOCUS)
- No existing transformer-based EEG denoising method addresses real-time processing
- 0/8 core papers report inference latency or model parameters
- BCI applications require <50ms latency; current methods provide no timing benchmarks
- Trend toward increasingly complex architectures (dual-branch, ensemble, GAN) exacerbates this

**Evidence:** "Computational complexity not explicitly addressed" (Chuang et al., 2024); "Increased model complexity may limit clinical deployment" (Tang et al., 2025); "Computational cost scales quadratically with sequence length" (Abibullaev et al., 2023)

### GAP_002: Clinical Validation (CRITICAL - SECONDARY)
- All methods validated on semi-simulated datasets (EEGdenoiseNet)
- 0/8 core papers use clinical EEG recordings
- Real-world artifacts are non-stationary, overlapping, patient-specific

### GAP_003: Cross-Dataset Generalization (MODERATE)
- Models trained and tested on same data distribution
- No systematic domain adaptation or transfer learning studies

---

## HYPOTHESIS & STUDY AIMS

### Primary Hypothesis
A lightweight transformer architecture utilizing Flash Attention and channel-wise linear projection can achieve real-time EEG denoising (inference latency <10ms on GPU) while maintaining state-of-the-art performance (correlation coefficient >0.95 on EEGdenoiseNet), representing a >10x speedup over existing methods.

### Research Questions
1. Can efficient transformer variants achieve comparable performance while reducing computational cost?
2. What is the minimum latency achievable for transformer-based EEG denoising?
3. What is the optimal performance-efficiency trade-off?
4. Can the model be deployed on edge devices for wearable BCI applications?

### Study Aims
1. Design a lightweight EEG transformer architecture optimized for efficiency
2. Benchmark computational performance (latency, FLOPs, parameters) against SOTA
3. Establish efficiency metrics as standard evaluation criteria
4. Demonstrate edge deployment feasibility

---

## REQUIRED STRUCTURE

Write the Introduction with these sections (use subheadings):

### 1. Opening Context (~400 words)
- EEG importance in neuroscience and clinical applications
- Artifact contamination as fundamental challenge
- Traditional methods (ICA, wavelet) and their limitations
- Cite: (Puce & Hämäläinen, 2017), (Sadiq et al., 2019)

### 2. Deep Learning Revolution in EEG (~500 words)
- CNN and RNN approaches for EEG processing
- Limitations of these approaches for artifact removal
- Cite: (Rakhmatulin et al., 2024), (Malekzadeh et al., 2021), (Samal & Hashmi, 2024)

### 3. Transformer Emergence for EEG Denoising (~600 words)
- Transformer architecture advantages for temporal modeling
- Self-attention for capturing long-range dependencies
- Foundational work: EEGDnet (2022)
- Pure transformer approaches: ART (2024)
- Cite: (Pu et al., 2022), (Chuang et al., 2024), (Gowtham Reddy et al., 2024), (Abibullaev et al., 2023)

### 4. CNN-Transformer Hybrids and Recent Advances (~500 words)
- Motivation for hybrid architectures
- CT-DCENet, GCTNet, EEGDfus, DHCT-GAN
- Performance achievements (CC >0.98)
- Cite: (Tang et al., 2025), (Yin et al., 2025), (Huang et al., 2025), (Cai et al., 2025), (Chuang et al., 2025)

### 5. Critical Gap: Computational Efficiency (~400 words)
- Summarize GAP_001: No papers address real-time processing
- Quantify the void: 0/8 papers report latency
- Explain why this matters for BCI deployment
- Bridge to study rationale

### 6. Study Rationale and Aims (~400 words)
- Present the research gap as opportunity
- State primary hypothesis
- List specific aims (4 aims)
- Preview contributions (theoretical, practical, methodological)

---

## CRITICAL CONSTRAINTS (ANTI-HALLUCINATION)

1. **ONLY cite papers from the Paper Manifest above** - Do NOT invent citations
2. **Use exact APA 7 format**: (Author et al., Year) or Author et al. (Year)
3. **Do NOT fabricate statistics** - Only use numbers explicitly provided
4. **Stay within scope**: Focus on EEG denoising, transformers, and efficiency
5. **Avoid claims about papers not in manifest** - No mentions of other methods unless cited
6. **Do NOT claim clinical validation exists** - This is identified as a gap

### Allowed Statistics (from paper manifest):
- EEGDnet: 18% and 11% improvements in CC for ocular and muscle artifacts (Pu et al., 2022)
- GCTNet: 11.15% RRMSE reduction, 9.81% SNR improvement for EMG (Yin et al., 2025)
- CT-DCENet: 0.79 dB SNR improvement, 1.9% RRMSE reduction for mixed artifacts (Tang et al., 2025)
- EEGDfus: CC = 0.983 and 0.992 on EEGdenoiseNet and SSED (Huang et al., 2025)
- Motor imagery classification: 95.2% accuracy (Sadiq et al., 2019)
- Seizure detection: 99.71% accuracy (Malekzadeh et al., 2021)

---

## OUTPUT FORMAT

Write the complete Introduction section in academic prose. Include:
- Proper paragraph structure (no bullet points in final text)
- Smooth transitions between sections
- In-text citations in APA 7 format
- A final paragraph clearly stating the study's contributions

---

## BEGIN WRITING

Write the complete Introduction section now, following the structure and constraints above.
