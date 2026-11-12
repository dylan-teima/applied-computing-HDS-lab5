"""Stack unrelated cohorts with provenance; never invent a patient linkage."""
import csv
import sys
rows = []
for path, source, key in [(sys.argv[1], 'lab3', 'sample_id'), (sys.argv[2], 'lab4', 'patient_id')]:
    with open(path, newline='') as f:
        rows.extend({'record_id': source+':'+r[key], 'source': source, **r} for r in csv.DictReader(f))
columns = list(dict.fromkeys(k for r in rows for k in r))
assert len({r['record_id'] for r in rows}) == len(rows)
with open(sys.argv[3], 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
    w.writeheader(); w.writerows(rows)
print(f'Combined {len(rows)} source-labeled records')
