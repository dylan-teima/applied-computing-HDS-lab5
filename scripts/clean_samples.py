"""Lab 3 scalar cleaning rules, adapted to the standard library."""
import csv
import re
import sys
from datetime import datetime
def norm_sample_id(x):
    s = x.strip()
    m = re.search(r"(\d+)$", s)
    return f"S{int(m.group(1)):04d}" if m else s.upper()


def parse_dob(x):
    s = x.strip()
    formats = [
        (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),
        (r"^\d{2}/\d{2}/\d{4}$", "%m/%d/%Y"),
        (r"^\d{2}-[A-Za-z]{3}-\d{4}$", "%d-%b-%Y"),
        (r"^\d{2}\.\d{2}\.\d{2}$", "%m.%d.%y"),
    ]
    for pattern, fmt in formats:
        if re.match(pattern, s):
            try:
                return datetime.strptime(s, fmt).strftime("%Y-%m-%d"), "parsed_by_rule"
            except ValueError:
                return "", "invalid_date"
    return "", "unparsed"


def norm_sex(s):
    x = s.strip().lower()
    if x in {"m", "male"}:
        return "Male"
    if x in {"f", "female"}:
        return "Female"
    return "Unknown"


def norm_site(s):
    x = re.sub(r"[\s_-]+", "", s.strip().lower())
    return {"sitea": "Site A", "siteb": "Site B", "sitec": "Site C"}.get(x, s.strip())


def clean_glucose(value, unit):
    raw_value = value.strip()
    flag = "*" if raw_value.endswith("*") else ""
    numeric_text = raw_value.rstrip("*").strip()

    if numeric_text.upper() in {"", "NA", "N/A"}:
        return None, flag, "missing"

    try:
        numeric = float(numeric_text)
    except ValueError:
        return None, flag, "unparsed_value"

    unit_norm = unit.strip().lower()
    if unit_norm == "mmol/l":
        mg_dl = numeric * 18.0182
    elif unit_norm == "mg/dl":
        mg_dl = numeric
    else:
        return None, flag, "unknown_unit"

    qc = "review_unit_or_value" if mg_dl < 20 or mg_dl > 600 else "ok"
    return round(mg_dl, 1), flag, qc



with open(sys.argv[1], newline='') as f:
    rows = list(csv.DictReader(f))
result = []
for r in rows:
    dob, status = parse_dob(r['dob'])
    glucose, flag, qc = clean_glucose(r['glucose_value'], r['glucose_unit'])
    result.append({**{k+'_raw': v for k,v in r.items()},
        'sample_id': norm_sample_id(r['sample_id']), 'dob': dob,
        'dob_parse_status': status, 'sex': norm_sex(r['sex']),
        'enrollment_site': norm_site(r['enrollment_site']),
        'glucose_mg_dl': glucose, 'glucose_flag': flag, 'glucose_qc': qc})
assert len({r['sample_id'] for r in result}) == len(result), 'Duplicate normalized sample IDs'
with open(sys.argv[2], 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(result[0]), lineterminator='\n')
    w.writeheader(); w.writerows(result)
print(f'Cleaned {len(result)} samples')
