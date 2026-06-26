#!/usr/bin/env python3
"""
01_clean_data.py
ENCePP AI Survey — convert raw Formspree JSON export into a tidy, analysis-ready CSV.

Input : data/raw_export.json   (Formspree export; 16 submissions, 121 fields)
Output: data/survey_clean.csv  (one row per respondent, labelled columns)
        data/codebook.csv      (variable dictionary)

The raw export stores multi-select answers as ' | '-separated strings and
the per-activity Q22 matrix as q22pv-<i>/q22pe-<i> cells whose value is a
comma/space list of {using, pilot, planned}. This script normalises all of it.
"""
import json
import csv
import os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw_export.json")
OUT = os.path.join(ROOT, "data", "survey_clean.csv")
CODEBOOK = os.path.join(ROOT, "data", "codebook.csv")

MULTI_SEP = " | "

# ----------------------------------------------------------------------
# Human-readable value labels (mirrors the survey HTML)
# ----------------------------------------------------------------------
LABELS = {
    "gate": {"PV": "Pharmacovigilance", "PE": "Pharmacoepidemiology"},
    "q21": {
        "yes-routine": "Yes - routine use",
        "yes-pilot": "Yes - pilot/evaluation",
        "no-planned": "No - planning within 2 years",
        "no-none": "No - no plans",
        "dk": "Don't know",
    },
    "q3": {
        "pharma": "Pharmaceutical company",
        "biotech": "Biotechnology company",
        "cro": "CRO",
        "regulator": "Regulatory agency",
        "academic": "Academic / research institution",
        "hospital": "Hospital / healthcare provider",
        "consulting": "Consulting firm",
        "other-org": "Other organisation",
    },
    "q1": {
        "ps-assoc": "Patient/Drug Safety Associate",
        "ps-sr": "Senior Patient/Drug Safety Specialist",
        "ps-mgr": "Patient/Drug Safety Manager",
        "ps-head": "Head/VP/Director of Drug Safety",
        "qppv": "QPPV",
        "researcher-pv": "PV researcher",
        "reg-assessor": "Regulatory assessor (PV)",
        "cro-pv": "PV specialist at CRO",
        "medical-affairs": "Medical Affairs / PV",
        "other-pv": "Other (PV)",
        "researcher-pe": "PE researcher",
        "sr-researcher": "Senior researcher",
        "assoc-prof": "Associate professor",
        "professor": "Full professor",
        "pe-industry": "Epidemiologist/RWE (industry)",
        "pe-regulator": "Regulatory assessor (PE)",
        "pe-cro": "Epidemiologist/RWE at CRO (PE)",
        "pe-hta": "HTA / Outcomes Research",
        "data-scientist-pe": "Data scientist (PE)",
        "other-pe": "Other (PE)",
    },
}

# Activity labels for the Q22 matrices
Q22_PV = [
    "Signal detection (ICSRs)", "Signal detection (literature)",
    "Case processing (intake/triage)", "Narrative writing/summarisation",
    "Causality assessment", "MedDRA/terminology coding",
    "Conversational AI (reporter follow-up)", "Benefit-risk assessment",
    "RMP development", "PSUR/PBRER generation/review",
    "Risk minimisation evaluation", "Regulatory writing",
    "Reports/articles/figures",
]
Q22_PE = [
    "Literature screening (evidence synthesis)", "Literature screening (signal eval.)",
    "Variable definition/phenotyping", "Drug utilisation analysis",
    "Predictive modelling (ADR/outcomes)", "Causal inference (AI-supported)",
    "Study design/feasibility", "Outcome ascertainment/misclassification",
    "Benefit-risk assessment", "Risk minimisation evaluation",
    "Regulatory writing", "Reports/articles/figures",
]

LIKERT5 = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "": None}


def split_multi(val):
    if not val:
        return []
    return [v.strip() for v in str(val).split(MULTI_SEP) if v.strip()]


def main():
    with open(RAW, encoding="utf-8") as f:
        data = json.load(f)
    subs = data["submissions"]

    rows = []
    for i, s in enumerate(subs):
        r = OrderedDict()
        r["respondent_id"] = f"R{i+1:02d}"
        track = s.get("gate", "")
        r["track"] = LABELS["gate"].get(track, track)
        r["track_code"] = track

        # profile
        r["role_code"] = s.get("q1", "")
        r["role"] = LABELS["q1"].get(s.get("q1", ""), s.get("q1", ""))
        r["org_code"] = s.get("q3", "")
        r["organisation"] = LABELS["q3"].get(s.get("q3", ""), s.get("q3", ""))
        r["country"] = s.get("q3a", "")
        r["pv_team_size"] = s.get("q4", "")
        r["offshelf_ai"] = s.get("q_offshelf", "")

        # adoption
        r["adoption_code"] = s.get("q21", "")
        r["adoption"] = LABELS["q21"].get(s.get("q21", ""), s.get("q21", ""))

        # AI methods (multi)
        methods = split_multi(s.get("q23b", ""))
        r["methods"] = ";".join(methods)
        r["n_methods"] = len([m for m in methods if m not in ("none-method", "use-not-know")])

        # aspirational priorities (multi, up to 3)
        wishes = split_multi(s.get("q24", ""))
        r["wishes"] = ";".join(wishes)

        # PE / PV applications explored (multi)
        r["pe_apps"] = ";".join(split_multi(s.get("q5pe", "")))
        r["pv_apps"] = ";".join(split_multi(s.get("q5pv", "")))

        # frequency
        r["pe_freq"] = s.get("q9pe", "")
        r["pv_freq"] = s.get("q9pv", "")

        # PE-specific
        r["genai_changed_pe"] = s.get("q7pe", "")
        r["interoperability"] = s.get("q8pe", "")

        # Q22 matrices -> count "currently using" per respondent
        for j, lab in enumerate(Q22_PV):
            cell = s.get(f"q22pv-{j}", "")
            statuses = split_multi(cell) or [c.strip() for c in str(cell).split(",") if c.strip()]
            r[f"q22pv_{j:02d}_using"] = int("using" in statuses)
            r[f"q22pv_{j:02d}_pilot"] = int("pilot" in statuses)
            r[f"q22pv_{j:02d}_planned"] = int("planned" in statuses)
        for j, lab in enumerate(Q22_PE):
            cell = s.get(f"q22pe-{j}", "")
            statuses = split_multi(cell) or [c.strip() for c in str(cell).split(",") if c.strip()]
            r[f"q22pe_{j:02d}_using"] = int("using" in statuses)
            r[f"q22pe_{j:02d}_pilot"] = int("pilot" in statuses)
            r[f"q22pe_{j:02d}_planned"] = int("planned" in statuses)

        # data sources (multi)
        r["data_sources"] = ";".join(split_multi(s.get("q23a", "")))

        # infrastructure single-choice items
        for k in ["qi1", "qi2", "qi3", "qi4", "qi5", "qi6", "qi7",
                  "qi8", "qi9", "qi10", "qi11", "qi12", "qi13", "qi14",
                  "qi15", "qi16", "qi17"]:
            r[k] = s.get(k, "")

        # terminology familiarity (1-5)
        for term in ["ml", "nlp", "llm", "pred", "sig"]:
            r[f"term_{term}"] = LIKERT5.get(str(s.get(f"term-{term}", "")), None)

        # perceptions (1-5)
        for pk in ["genai", "ethics", "jobs", "reg", "ready", "trust"]:
            r[f"p_{pk}"] = LIKERT5.get(str(s.get(f"p-{pk}", "")), None)

        # conversational AI comfort
        r["conv_ai_comfort"] = s.get("qp2", "")

        # enablers (multi, up to 3)
        r["enablers"] = ";".join(split_multi(s.get("qp3", "")))

        rows.append(r)

    # write tidy CSV
    fieldnames = list(rows[0].keys())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {len(rows)} rows x {len(fieldnames)} cols -> {OUT}")

    # codebook
    cb = [
        ("respondent_id", "Anonymous respondent identifier"),
        ("track", "Survey track (PV or PE), from screening question Q0"),
        ("role", "Respondent role (Q1a)"),
        ("organisation", "Organisation type (Q1b)"),
        ("country", "Country of organisation (Q3a)"),
        ("pv_team_size", "PV function size, PV track only (Q4)"),
        ("offshelf_ai", "Off-the-shelf AI use in organisation (cover item)"),
        ("adoption", "Organisational AI adoption status (Q21)"),
        ("methods", "AI methods used, ';'-separated (Q23b)"),
        ("wishes", "Aspirational AI priorities, up to 3 (Q24)"),
        ("pe_apps", "PE AI applications explored (Q5-PE)"),
        ("pv_apps", "PV AI aspects explored (Q5-PV)"),
        ("genai_changed_pe", "Belief generative AI changed PE (Q6-PE)"),
        ("interoperability", "AI interoperability w/ CDM/terminologies (Q7-PE)"),
        ("q22pv_NN_using/pilot/planned", "PV activity matrix status flags (Q22-PV)"),
        ("q22pe_NN_using/pilot/planned", "PE activity matrix status flags (Q22-PE)"),
        ("data_sources", "Data sources used for AI (I-DS / Q23a)"),
        ("qi1", "Single most critical barrier (I-1)"),
        ("qi2..qi17", "Infrastructure/governance/skills single-choice items"),
        ("term_*", "Terminology familiarity 1-5 (I-18)"),
        ("p_*", "Perception Likert 1-5 (P-1)"),
        ("conv_ai_comfort", "Comfort implementing conversational AI (P-2)"),
        ("enablers", "Enabling factors, up to 3 (P-3)"),
    ]
    with open(CODEBOOK, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["variable", "description"])
        w.writerows(cb)
    print(f"Wrote codebook -> {CODEBOOK}")


if __name__ == "__main__":
    main()
