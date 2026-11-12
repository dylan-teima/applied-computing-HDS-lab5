"""Reuse Lab 4 SQL; preserve patient grain and missing clinical values."""
import csv
from pathlib import Path
import sqlite3
import sys

with sqlite3.connect(Path(sys.argv[1]).resolve().as_uri()+'?mode=ro', uri=True) as con:
    con.row_factory = sqlite3.Row
    assert con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert not con.execute('PRAGMA foreign_key_check').fetchall()
    assert not con.execute('SELECT patient_id FROM samples GROUP BY patient_id HAVING COUNT(*)>1').fetchall(), 'Multiple samples per patient require a selection policy'
    clinical = [dict(r) for r in con.execute(Path(sys.argv[2]).read_text())]
    counts = {}
    for r in con.execute(Path(sys.argv[3]).read_text()):
        counts.setdefault(r['patient_id'], {})[r['gene_symbol']] = r['mutation_count']
    result = [{**r, **counts[r['patient_id']]} for r in clinical]
    assert len(result) == con.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
    assert len({r['patient_id'] for r in result}) == len(result)
with open(sys.argv[4], 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(result[0]), lineterminator='\n')
    w.writeheader(); w.writerows(result)
print(f'Queried {len(result)} patients')
