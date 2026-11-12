"""Reproduce clean/partial/restored/no-op runs and assert branch isolation."""
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
if Path.cwd() != root:
    raise SystemExit('Run from the repository root')
evidence = Path('evidence'); evidence.mkdir(exist_ok=True)
def run(name):
    command = [sys.executable, '-m', 'snakemake', '--cores', '2', '--printshellcmds']
    p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (evidence/name).write_text('$ python -m snakemake --cores 2 --printshellcmds\n'+p.stdout)
    if p.returncode:
        raise RuntimeError(f'Workflow failed; see evidence/{name}')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def snapshot():
    return {str(p): {'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns} for p in sorted(Path('outputs').glob('*'))}
shutil.rmtree('outputs', ignore_errors=True)
run('01_clean_run.log')
before = snapshot()
raw = Path('data/raw/lab3-messy-data/messy_samples.csv')
original = raw.read_bytes()
try:
    reader = csv.DictReader(io.StringIO(original.decode()))
    fields = reader.fieldnames; rows = list(reader)
    # Use a known mg/dL value so the report median changes too.
    row = next(r for r in rows if r['glucose_unit'].strip().lower()=='mg/dl')
    old = row['glucose_value']; row['glucose_value'] = '111.1' if old != '111.1' else '112.1'
    with raw.open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)
    run('02_partial_run.log')
    after = snapshot()
    assert before['outputs/patient_features.csv'] == after['outputs/patient_features.csv'], 'Query branch unexpectedly reran'
    for name in ['cleaned_samples.csv','combined_features.csv','summary.txt','report.html']:
        assert before['outputs/'+name]['mtime_ns'] != after['outputs/'+name]['mtime_ns'], name
    assert before['outputs/combined_features.csv']['sha256'] != after['outputs/combined_features.csv']['sha256']
    audit = {'change': {'sample_id':row['sample_id'], 'old_glucose_value':old, 'new_glucose_value':row['glucose_value']}, 'before':before,'after_partial':after}
finally:
    raw.write_bytes(original)
run('03_restored_run.log')
restored=snapshot()
assert all(before[p]['sha256']==restored[p]['sha256'] for p in before), 'Restored output differs'
run('04_noop_run.log')
assert snapshot()==restored, 'No-op changed outputs'
audit['restored_outputs_match_clean_run']=True
audit['raw_sha256']=sha(raw)
audit['noop_outputs_unchanged']=True
(evidence/'verification.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS: clean, partial, restored, and no-op runs; query branch unchanged; restored hashes match.')
