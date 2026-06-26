#!/usr/bin/env python3
"""
02_analyse.py
ENCePP AI Survey — descriptive analysis and figure generation.

Reproduces all counts cited in the Results section and writes:
  - figures/figure1_adoption.png
  - figures/figure2a_pv_activities.png
  - figures/figure2b_pe_activities.png
  - figures/figure3_methods.png
  - figures/figure4_priorities.png
  - figures/figure5_barriers.png
  - figures/figure6_perceptions_terminology.png
  - outputs/table1_respondent_profile.csv
  - outputs/results_summary.txt
"""
import os
import csv
from collections import Counter, OrderedDict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLEAN = os.path.join(ROOT, "data", "survey_clean.csv")
FIG = os.path.join(ROOT, "figures")
OUT = os.path.join(ROOT, "outputs")
os.makedirs(FIG, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# ── House style ────────────────────────────────────────────────
NAVY = "#1C3557"; MID = "#2E6DA4"; TEAL = "#1A8FA0"
GOLD = "#C9852A"; GREEN = "#1A7A4A"; PURPLE = "#6C3483"
GREY = "#8298AE"
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": "#5A6B7B",
    "axes.linewidth": 0.8,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelcolor": NAVY,
    "axes.titlecolor": NAVY,
    "xtick.color": "#3A4A58",
    "ytick.color": "#3A4A58",
    "figure.dpi": 140,
})

# ── Load ───────────────────────────────────────────────────────
def load():
    with open(CLEAN, encoding="utf-8") as f:
        return list(csv.DictReader(f))

rows = load()
PE = [r for r in rows if r["track_code"] == "PE"]
PV = [r for r in rows if r["track_code"] == "PV"]
N, nPE, nPV = len(rows), len(PE), len(PV)

log = []
def note(msg):
    log.append(msg); print(msg)

note(f"Total respondents: {N} (PE={nPE}, PV={nPV})")

# ── Figure 1: adoption status ──────────────────────────────────
adopt_order = ["yes-routine", "yes-pilot", "no-planned", "no-none", "dk"]
adopt_lab = {"yes-routine": "Routine use", "yes-pilot": "Pilot / evaluation",
             "no-planned": "Planning (<2 yr)", "no-none": "No plans", "dk": "Don't know"}
adopt = Counter(r["adoption_code"] for r in rows)
note(f"Adoption: {dict(adopt)}")
vals = [adopt.get(k, 0) for k in adopt_order]
fig, ax = plt.subplots(figsize=(7, 3.2))
colors = [GREEN, TEAL, GOLD, "#C0392B", GREY]
bars = ax.barh([adopt_lab[k] for k in adopt_order][::-1], vals[::-1],
               color=colors[::-1], edgecolor="white")
for b, v in zip(bars, vals[::-1]):
    if v: ax.text(v + 0.1, b.get_y() + b.get_height()/2, str(v), va="center", fontweight="bold", color=NAVY)
ax.set_xlabel("Number of respondents")
ax.set_title("Figure 1. Organisational AI adoption status (N=16)")
ax.set_xlim(0, max(vals) + 1)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "figure1_adoption.png"), bbox_inches="tight"); plt.close()

# ── Figure 2: activity matrices (PV and PE) ────────────────────
Q22_PV = ["Signal detection (ICSRs)", "Signal detection (lit.)", "Case processing",
          "Narrative writing", "Causality assessment", "MedDRA coding",
          "Conversational AI", "Benefit-risk", "RMP development", "PSUR/PBRER",
          "Risk minimisation", "Regulatory writing", "Reports/articles"]
Q22_PE = ["Lit. screening (synth.)", "Lit. screening (signal)", "Phenotyping",
          "Drug utilisation", "Predictive modelling", "Causal inference",
          "Study design", "Outcome ascertainment", "Benefit-risk",
          "Risk minimisation", "Regulatory writing", "Reports/articles"]

def activity_counts(subset, prefix, n_acts):
    using = []; pilot = []; planned = []
    for j in range(n_acts):
        u = sum(int(r.get(f"{prefix}_{j:02d}_using", 0)) for r in subset)
        p = sum(int(r.get(f"{prefix}_{j:02d}_pilot", 0)) for r in subset)
        pl = sum(int(r.get(f"{prefix}_{j:02d}_planned", 0)) for r in subset)
        using.append(u); pilot.append(p); planned.append(pl)
    return using, pilot, planned

def stacked_activity(labels, subset, prefix, title, fname):
    using, pilot, planned = activity_counts(subset, prefix, len(labels))
    order = np.argsort([u + p + pl for u, p, pl in zip(using, pilot, planned)])
    labels = [labels[i] for i in order]
    using = [using[i] for i in order]; pilot = [pilot[i] for i in order]; planned = [planned[i] for i in order]
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(7.5, 0.42*len(labels)+1.2))
    ax.barh(y, using, color=TEAL, edgecolor="white", label="Currently using")
    ax.barh(y, pilot, left=using, color=MID, edgecolor="white", label="Pilot")
    ax.barh(y, planned, left=[u+p for u, p in zip(using, pilot)], color=GOLD, edgecolor="white", label="Planned")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Number of respondents")
    ax.set_title(title)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    maxv = max([u+p+pl for u, p, pl in zip(using, pilot, planned)] + [1])
    ax.set_xlim(0, maxv + 1)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, fname), bbox_inches="tight"); plt.close()

stacked_activity(Q22_PV, PV, "q22pv", f"Figure 2a. AI activities in pharmacovigilance (n={nPV})", "figure2a_pv_activities.png")
stacked_activity(Q22_PE, PE, "q22pe", f"Figure 2b. AI activities in pharmacoepidemiology (n={nPE})", "figure2b_pe_activities.png")

# ── PE applications (Q5-PE) for results text ───────────────────
pe_app_lab = {
    "phenotyping": "Disease phenotyping", "outcome-asc": "Outcome ascertainment",
    "study-design": "AI-assisted study design", "causal": "Causal inference / TTE",
    "nlp-texts": "NLP on clinical text", "data-extract": "Data extraction/lit. synthesis",
    "prediction": "Predictive modelling", "literature": "Literature screening",
    "drug-util": "Drug utilisation", "benefit-risk": "Benefit-risk",
    "reg-writing": "Regulatory writing", "reports": "Reports/articles",
}
pe_apps = Counter()
for r in PE:
    for a in r["pe_apps"].split(";"):
        if a and a not in ("none-pe", "dk-q5pe"):
            pe_apps[a] += 1
note(f"PE apps (Q5-PE): {dict(pe_apps)}")

# ── Figure 3: AI methods (Q23b) ────────────────────────────────
meth_lab = {
    "classical-ml": "Classical ML", "deep-learning": "Deep learning",
    "nlp": "NLP", "llm": "Large language models", "hybrid-causal": "Hybrid causal-AI",
    "federated": "Federated/privacy-preserving", "xai": "Explainable AI",
    "generative": "Generative AI", "signal-algo": "Signal detection algorithms",
    "use-not-know": "Use AI, method unknown", "other-method": "Other", "none-method": "None",
}
def method_counts(subset):
    c = Counter()
    for r in subset:
        for m in r["methods"].split(";"):
            if m: c[m] += 1
    return c
mPE = method_counts(PE); mPV = method_counts(PV)
note(f"PE methods: {dict(mPE)}")
note(f"PV methods: {dict(mPV)}")
keys = [k for k in meth_lab if (mPE.get(k, 0) + mPV.get(k, 0)) > 0]
keys = sorted(keys, key=lambda k: mPE.get(k, 0) + mPV.get(k, 0))
y = np.arange(len(keys))
fig, ax = plt.subplots(figsize=(7.5, 0.42*len(keys)+1.2))
ax.barh(y - 0.2, [mPE.get(k, 0) for k in keys], height=0.4, color=TEAL, label=f"PE (n={nPE})", edgecolor="white")
ax.barh(y + 0.2, [mPV.get(k, 0) for k in keys], height=0.4, color=PURPLE, label=f"PV (n={nPV})", edgecolor="white")
ax.set_yticks(y); ax.set_yticklabels([meth_lab[k] for k in keys], fontsize=9)
ax.set_xlabel("Number of respondents")
ax.set_title("Figure 3. AI methods used or developed, by track")
ax.legend(fontsize=8, frameon=False, loc="lower right")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "figure3_methods.png"), bbox_inches="tight"); plt.close()

# ── Figure 4: aspirational priorities (Q24) ────────────────────
wish_lab = {
    "signal-scale": "Automated signal detection at scale",
    "realtime-pv": "Real-time PV from EHR/claims",
    "br-ai": "AI-assisted benefit-risk",
    "causal-auto": "Automated causal inference",
    "llm-coding": "LLM-based AE coding",
    "federated-wish": "Federated learning",
    "xai-reg": "Explainable AI for regulation",
    "multimodal": "Multi-modal data integration",
    "protocol-ai": "Protocol feasibility/cohort ID",
    "synthetic-wish": "Generative AI for synthetic data",
    "other-wish": "Other", "dk-wish": "Don't know",
}
def wish_counts(subset):
    c = Counter()
    for r in subset:
        for w in r["wishes"].split(";"):
            if w and w != "dk-wish": c[w] += 1
    return c
wPE = wish_counts(PE); wPV = wish_counts(PV)
note(f"PE wishes: {dict(wPE)}")
note(f"PV wishes: {dict(wPV)}")
keys = [k for k in wish_lab if (wPE.get(k, 0)+wPV.get(k, 0)) > 0 and k != "dk-wish"]
keys = sorted(keys, key=lambda k: wPE.get(k, 0)+wPV.get(k, 0))
y = np.arange(len(keys))
fig, ax = plt.subplots(figsize=(7.5, 0.42*len(keys)+1.2))
ax.barh(y - 0.2, [wPE.get(k, 0) for k in keys], height=0.4, color=TEAL, label=f"PE (n={nPE})", edgecolor="white")
ax.barh(y + 0.2, [wPV.get(k, 0) for k in keys], height=0.4, color=PURPLE, label=f"PV (n={nPV})", edgecolor="white")
ax.set_yticks(y); ax.set_yticklabels([wish_lab[k] for k in keys], fontsize=9)
ax.set_xlabel("Number of respondents (up to 3 selections each)")
ax.set_title("Figure 4. AI capabilities respondents most want to develop")
ax.legend(fontsize=8, frameon=False, loc="lower right")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "figure4_priorities.png"), bbox_inches="tight"); plt.close()

# ── Figure 5: barriers (I-1) ───────────────────────────────────
bar_lab = {
    "computing": "Computing resources", "data": "Data access",
    "expertise": "AI expertise", "governance": "Governance/reg. clarity",
    "funding": "Funding", "maintenance": "System maintenance",
    "leadership": "Leadership support", "privacy": "Privacy/security/ethics",
    "culture": "Organisational culture", "none": "No barriers",
    "other-barrier": "Other", "dk": "Don't know",
}
barr = Counter(r["qi1"] for r in rows if r["qi1"])
note(f"Barriers (I-1): {dict(barr)}")
keys = sorted([k for k in barr if barr[k] > 0], key=lambda k: barr[k])
y = np.arange(len(keys))
fig, ax = plt.subplots(figsize=(7, 0.42*len(keys)+1.2))
bars = ax.barh(y, [barr[k] for k in keys], color=NAVY, edgecolor="white")
for b, k in zip(bars, keys):
    ax.text(barr[k]+0.08, b.get_y()+b.get_height()/2, str(barr[k]), va="center", fontweight="bold", color=NAVY)
ax.set_yticks(y); ax.set_yticklabels([bar_lab.get(k, k) for k in keys], fontsize=9)
ax.set_xlabel("Number of respondents")
ax.set_title("Figure 5. Single most critical barrier to AI adoption (N=16)")
ax.set_xlim(0, max(barr.values())+1)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "figure5_barriers.png"), bbox_inches="tight"); plt.close()

# ── Figure 6: perceptions + terminology (means by track) ───────
perc_keys = ["p_genai", "p_ethics", "p_jobs", "p_reg", "p_ready", "p_trust"]
perc_lab = ["GenAI potential", "Ethics/transparency", "Job security threat",
            "Regulatory clarity", "Org. readiness", "Trust in outputs"]
term_keys = ["term_ml", "term_nlp", "term_llm", "term_pred", "term_sig"]
term_lab = ["Machine learning", "NLP", "Large language models",
            "Predictive analytics", "Signal detection algos"]

def means(subset, keys):
    out = []
    for k in keys:
        vals = [float(r[k]) for r in subset if r[k] not in ("", "None", None)]
        out.append(np.mean(vals) if vals else np.nan)
    return out

pe_perc = means(PE, perc_keys); pv_perc = means(PV, perc_keys)
pe_term = means(PE, term_keys); pv_term = means(PV, term_keys)
note(f"PE perceptions means: {[round(x,1) for x in pe_perc]}")
note(f"PV perceptions means: {[round(x,1) for x in pv_perc]}")
note(f"PE terminology means: {[round(x,1) for x in pe_term]}")
note(f"PV terminology means: {[round(x,1) for x in pv_term]}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2))
yp = np.arange(len(perc_lab))
ax1.barh(yp-0.2, pe_perc, height=0.4, color=TEAL, label=f"PE (n={nPE})", edgecolor="white")
ax1.barh(yp+0.2, pv_perc, height=0.4, color=PURPLE, label=f"PV (n={nPV})", edgecolor="white")
ax1.set_yticks(yp); ax1.set_yticklabels(perc_lab, fontsize=9)
ax1.set_xlim(0, 5); ax1.set_xlabel("Mean Likert score (1-5)")
ax1.set_title("Figure 6a. Perceptions, by track")
ax1.legend(fontsize=8, frameon=False, loc="lower right")
ax1.spines[["top", "right"]].set_visible(False)
yt = np.arange(len(term_lab))
ax2.barh(yt-0.2, pe_term, height=0.4, color=TEAL, label=f"PE (n={nPE})", edgecolor="white")
ax2.barh(yt+0.2, pv_term, height=0.4, color=PURPLE, label=f"PV (n={nPV})", edgecolor="white")
ax2.set_yticks(yt); ax2.set_yticklabels(term_lab, fontsize=9)
ax2.set_xlim(0, 5); ax2.set_xlabel("Mean familiarity (1-5)")
ax2.set_title("Figure 6b. Terminology familiarity, by track")
ax2.legend(fontsize=8, frameon=False, loc="lower right")
ax2.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "figure6_perceptions_terminology.png"), bbox_inches="tight"); plt.close()

# ── Table 1: respondent profile ────────────────────────────────
def col_counts(subset, field):
    return Counter(r[field] for r in subset if r[field])

t1 = []
t1.append(["Characteristic", "Level", f"Overall n (N={N})", "Overall %",
           f"PV n (n={nPV})", "PV %", f"PE n (n={nPE})", "PE %"])
def add_block(name, field):
    levels = sorted(set(r[field] for r in rows if r[field]),
                    key=lambda L: -sum(1 for r in rows if r[field] == L))
    for L in levels:
        o = sum(1 for r in rows if r[field] == L)
        v = sum(1 for r in PV if r[field] == L)
        e = sum(1 for r in PE if r[field] == L)
        t1.append([name, L, o, f"{100*o/N:.1f}", v, f"{100*v/nPV:.1f}" if nPV else "",
                   e, f"{100*e/nPE:.1f}" if nPE else ""])
        name = ""
add_block("Role", "role")
add_block("Organisation", "organisation")
add_block("Country", "country")
with open(os.path.join(OUT, "table1_respondent_profile.csv"), "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(t1)
note("Wrote Table 1 -> outputs/table1_respondent_profile.csv")

# ── Extra summary stats cited in Results ───────────────────────
note(f"Off-the-shelf AI use (any 'yes'): {sum(1 for r in rows if r['offshelf_ai'].startswith('yes'))}/{N}")
note(f"GenAI changed PE = yes: {sum(1 for r in PE if r['genai_changed_pe']=='yes')}/{nPE}")
interop = Counter(r["interoperability"] for r in PE if r["interoperability"])
note(f"PE interoperability: {dict(interop)}")
# enablers
enab = Counter()
for r in PE:
    for e in r["enablers"].split(";"):
        if e: enab[e] += 1
note(f"PE enablers (P-3): {dict(enab)}")
# conv AI comfort
note("PE conv-AI comfort: " + str(dict(Counter(r['conv_ai_comfort'] for r in PE))))
note("PV conv-AI comfort: " + str(dict(Counter(r['conv_ai_comfort'] for r in PV))))

with open(os.path.join(OUT, "results_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log))
print("\nAll figures and outputs written.")
