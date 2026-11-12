"""Write a standalone HTML report with inline SVG and a plain-text summary."""
import csv
from collections import Counter
from html import escape
from pathlib import Path
import statistics
import sys
with open(sys.argv[1], newline='') as f:
    rows = list(csv.DictReader(f))
samples = [r for r in rows if r['source']=='lab3']
patients = [r for r in rows if r['source']=='lab4']
qc = Counter(r['glucose_qc'] for r in samples)
genes = ['TP53','KRAS','EGFR','STK11','KEAP1']
carriers = {g: sum(int(r[g])>0 for r in patients) for g in genes}
valid = [float(r['glucose_mg_dl']) for r in samples if r['glucose_qc']=='ok']
summary = '\n'.join([
    'Lab 5 workflow summary',
    f'Combined records: {len(rows)}; Lab 3 samples: {len(samples)}; Lab 4 patients: {len(patients)}.',
    f'Glucose QC counts: {dict(sorted(qc.items()))}.',
    f'Median glucose among QC-ok samples (n={len(valid)}): {statistics.median(valid):.1f} mg/dL.',
    f'Patients missing stage: {sum(not r["stage"] for r in patients)}.',
    *[f'{g}: {n}/{len(patients)} patients with a recorded non-Silent mutation ({n/len(patients):.1%}).' for g,n in carriers.items()],
    'The datasets are unrelated: rows are stacked with source labels, not matched across cohorts.',
    'Blank cells mean missing or not applicable; gene zeros mean no eligible recorded mutation.',
    'Counts describe this dataset, not population prevalence. No clinical inference is made.',
    'DOB conventions follow Lab 3 (dot dates MM.DD.YY); ambiguous dates require source confirmation.',
    'Glucose uses recorded units literally; implausible values remain flagged and are excluded from the QC-ok median.'
])+'\n'
Path(sys.argv[2]).write_text(summary)
svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 300" role="img" aria-label="Patients with recorded non-Silent mutations"><rect width="760" height="300" fill="white"/>'
for i,(g,n) in enumerate(carriers.items()):
    y=30+i*52
    svg += f'<text x="15" y="{y+19}" font-size="16">{g}</text><rect x="100" y="{y}" width="{n/len(patients)*500:.2f}" height="28" fill="#206a8a"/><text x="{110+n/len(patients)*500:.2f}" y="{y+19}" font-size="15">{n} ({n/len(patients):.1%})</text>'
svg += '</svg>'
Path(sys.argv[3]).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Lab 5 summary</title><style>body{font:17px system-ui;max-width:900px;margin:40px auto;padding:0 24px;line-height:1.5}svg{width:100%}pre{white-space:pre-wrap}</style><h1>Lab 5: Reproducible cohort workflow</h1><h2>Recorded mutation carriers in Lab 4</h2>'+svg+'<h2>Summary and limitations</h2><pre>'+escape(summary)+'</pre></html>')
print(summary)
