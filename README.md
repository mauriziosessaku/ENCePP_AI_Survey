# ENCePP AI Survey — Analysis Repository

Reproducible analysis pipeline for the **ENCePP Working Group on AI in Pharmacoepidemiology and Pharmacovigilance** survey on the perception and use of artificial intelligence (AI) tools in pharmacoepidemiology (PE) and pharmacovigilance (PV).

This repository accompanies the manuscript *"Perception and use of AI in pharmacoepidemiology and pharmacovigilance: a community survey of the ENCePP Working Group on AI."* It contains the de-identified survey data, the cleaning and analysis code (in both **Python** and **R**), and the scripts that regenerate every figure and table reported in the manuscript.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Reproducible](https://img.shields.io/badge/analysis-reproducible-1A8FA0.svg)](#reproducing-the-analysis)

---

## Contents

```
encepp-ai-survey/
├── data/
│   ├── raw_export.json            # Raw survey export (de-identified, 16 responses)
│   ├── survey_clean.csv           # Tidy, analysis-ready dataset (one row/respondent)
│   └── codebook.csv               # Variable dictionary
├── python/
│   ├── 01_clean_data.py           # Raw JSON → tidy CSV + codebook
│   └── 02_analyse.py              # Descriptive analysis + all figures + Table 1
├── R/
│   └── analyse.R                  # R replication of the descriptive analysis
├── figures/                       # Generated figures (PNG)
├── outputs/                       # Generated tables + results summary
├── docs/
│   └── survey_instrument.md       # Full survey instrument (all items + options)
├── requirements.txt               # Python dependencies
├── DESCRIPTION                    # R dependencies
├── run_all.sh                     # One-command reproduction (Python pipeline)
├── LICENSE                        # CC BY 4.0
└── README.md
```

---

## The survey

The instrument was developed through a **modified Delphi process** across six revision rounds and comprises 43 structured items administered through a branching design (a screening question routes respondents to a PV or PE track; shared sections are completed by all). An optional structured AI-tool inventory captures detailed, citable tool descriptions. The complete instrument is reproduced in [`docs/survey_instrument.md`](docs/survey_instrument.md).

The survey was implemented in SurveyXact (data controller: University of Copenhagen), administered from 29 May 2026, and is fully GDPR-compliant. **No personally identifiable information is contained in this repository**; free-text fields that could be identifying have been removed from the public export.

---

## Reproducing the analysis

### Option A — Python (primary pipeline)

```bash
# 1. (optional) create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. run the full pipeline
bash run_all.sh
#    └─ runs python/01_clean_data.py  then  python/02_analyse.py
```

This regenerates `data/survey_clean.csv`, all figures in `figures/`, and `outputs/table1_respondent_profile.csv`.

### Option B — R (replication)

```r
# from the repository root
install.packages(c("tidyverse", "scales"))   # if needed
source("R/analyse.R")
```

The R script reads the same `data/survey_clean.csv` and reproduces the key figures and Table 1 (files suffixed `_R`).

---

## Outputs

| Figure | Content |
|--------|---------|
| Figure 1 | Organisational AI adoption status (N=16) |
| Figure 2a / 2b | AI activity matrices — PV and PE tracks |
| Figure 3 | AI methods used or developed, by track |
| Figure 4 | AI capabilities respondents most want to develop |
| Figure 5 | Single most critical barrier to AI adoption |
| Figure 6a / 6b | Perceptions and terminology familiarity, by track |

`outputs/table1_respondent_profile.csv` reproduces the respondent profile (Table 1), and `outputs/results_summary.txt` logs every count cited in the Results section.

---

## Key findings (pilot round, N=16)

- **Adoption is widespread**: 9/16 organisations use AI routinely and 5/16 in pilots; off-the-shelf AI use is near-universal (15/16).
- **Methods**: classical ML (8/13) and large language models (7/13) lead in PE; several respondents use AI without knowing the underlying method.
- **Top barrier**: availability of **AI expertise**, ahead of privacy/security and computing resources.
- **Shared priority**: **explainable AI** suitable for regulatory and evidence-based decision-making.
- **Perceptions**: ethics and transparency rated highest; regulatory clarity and trust in outputs rated lowest.

> These are exploratory, hypothesis-generating findings from a small internal pilot sample. They are **not** intended to support inferential claims.

---

## Citation

If you use this code or data, please cite the accompanying manuscript (citation to be added on acceptance) and this repository:

```
ENCePP Working Group on AI in Pharmacoepidemiology and Pharmacovigilance.
ENCePP AI Survey — Analysis Repository. 2026. https://github.com/<org>/encepp-ai-survey
```

## License

- **Code**: MIT (see `LICENSE`).
- **Data and figures**: Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contact

ENCePP Working Group on AI in Pharmacoepidemiology and Pharmacovigilance — corresponding author: Maurizio Sessa (maurizio@sund.ku.dk), University of Copenhagen.
