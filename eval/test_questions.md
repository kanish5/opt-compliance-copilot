# Eval Set — 20 Test Questions

Run these against `rag_chain.answer()` and manually grade each as Correct / Partially Correct / Wrong / Refused.
This is the source for the "X/20 correct" accuracy metric in the README and resume bullets — fill in the Result
column after running `eval/run_eval.py`.

| # | Question | Expected Source Doc | Result |
|---|----------|---------------------|--------|
| 1 | How many days can I be unemployed on regular post-completion OPT? | 02_90day_unemployment_rule | |
| 2 | Does the 90-day unemployment rule apply during pre-completion OPT? | 02_90day_unemployment_rule | |
| 3 | Do I need a job offer to apply for standard OPT? | 01_opt_overview | |
| 4 | How many months of STEM OPT extension can I get? | 03_stem_opt_extension | |
| 5 | What are the eligibility requirements for the STEM OPT extension? | 03_stem_opt_extension | |
| 6 | Can I do unpaid volunteer work while on the STEM OPT extension? | 03_stem_opt_extension | |
| 7 | How many days of unemployment are allowed during the STEM OPT extension? | 03_stem_opt_extension | |
| 8 | Does my employer need to be enrolled in E-Verify for the STEM extension? | 03_stem_opt_extension | |
| 9 | When do I need to submit my STEM OPT 6-month report? | 03_stem_opt_extension | |
| 10 | What form do I need for the STEM OPT training plan? | 03_stem_opt_extension | |
| 11 | How far in advance can I apply for the STEM OPT extension? | 03_stem_opt_extension | |
| 12 | What's the difference between CPT and OPT? | 04_cpt | |
| 13 | Does CPT require a separate EAD card? | 04_cpt | |
| 14 | If I use full-time CPT for 12 months, does that affect my OPT eligibility? | 04_cpt | |
| 15 | What is the window for applying for post-completion OPT relative to my graduation date? | 01_opt_overview | |
| 16 | Can I start working before I physically have my EAD card? | 01_opt_overview | |
| 17 | Within how many days of the DSO's OPT recommendation must USCIS receive my application? | 01_opt_overview | |
| 18 | What's the maximum total time (standard + STEM) I can be on OPT? | 03_stem_opt_extension | |
| 19 | What happens if I change employers during the STEM OPT extension? | 03_stem_opt_extension | |
| 20 | What is Curricular Practical Training used for? | 04_cpt | |

**Out-of-scope control questions** (the system should refuse these, not guess):
| # | Question | Expected Behavior |
|---|----------|--------------------|
| 21 | What's the H-1B cap for this fiscal year? | Refuse — outside source docs (F-1/OPT only, no H-1B docs ingested) |
| 22 | Can I travel internationally while my STEM OPT extension is pending? | Refuse or low-confidence — not covered by current 4 source docs, a real gap to fill by adding a travel-specific source doc |
