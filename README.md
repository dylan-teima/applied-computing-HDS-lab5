# Lab 5: Scalable Analysis workflow

This pipeline reuses the Lab 3 sample-cleaning rules and Lab 4
clinical/mutation SQL. All inputs and code are copied into this
repository, so running it does not require the sibling lab folders. The
saved run evidence uses Python 3.11.2 and Snakemake 8.30.0.

## Running the Analysis

Run these commands from this repository's root:

``` bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
snakemake --cores 2 --printshellcmds
```

A full clean run deletes only generated outputs:

``` bash
rm -rf outputs
snakemake --cores 2 --printshellcmds
```

To reproduce the complete clean/partial/restore/no-op experiment and its
saved console evidence:

``` bash
python scripts/prove_rerun.py
```

That script deletes the `outputs/` folder, runs the workflow, changes
one real glucose value in the local raw CSV, runs again, restores the
CSV in a `finally` block, reruns, and checks that a final invocation
does nothing. It overwrites the evidence files. To try a partial rerun
manually, edit a glucose value in
`data/raw/lab3-messy-data/messy_samples.csv`, save, then run:

``` bash
snakemake --cores 2 --printshellcmds
```

Only `clean_samples`, `combine`, and `report` should run. Editing the
database or either SQL file instead affects `query_patients`, `combine`,
and `report`. An unchanged invocation should report “Nothing to be
done.” Dry-run with `snakemake --cores 2 --dry-run`; export the graph
with `snakemake --dag > evidence/dag.dot` (Graphviz is optional for
rendering).

## Dependencies and scaling

``` mermaid
flowchart LR
    A[messy_samples.csv] --> C[clean_samples]
    B[cohort.db + two SQL files] --> Q[query_patients]
    C --> S[cleaned_samples.csv]
    Q --> P[patient_features.csv]
    S --> J[combine]
    P --> J
    J --> T[combined_features.csv]
    T --> R[report]
    R --> H[report.html + summary.txt]
```

Each rule declares its script as an input, together with every data/SQL
file it reads. Every produced artifact is an explicit output. The Python
interpreter and packages are environment dependencies captured by the
requirements files. Scripts use only Python's standard library and shell
paths are quoted for directories containing spaces.

The two initial branches are independent and can run concurrently with
`--cores 2` and each job uses one core. Using more cores does not speed
up these individual scripts or the serial combine/report stages. This
demonstrates dependency scheduling and selective recomputation, not a
large-data benchmark: current scripts materialize tables in memory, and
large datasets might require streaming or partitioned rules.

## Methods and outputs

- `outputs/cleaned_samples.csv`: one row per normalized Lab 3 sample,
  with original fields retained as `*_raw`. Regex rules standardize IDs,
  sex, site and four DOB formats. Dot dates use the inherited `MM.DD.YY`
  convention and Python's two-digit-year interpretation; ambiguous dates
  need source confirmation. Glucose uses the recorded unit, converting
  mmol/L by 18.0182, preserving `*` flags and marking values outside
  20–600 mg/dL for review. Values may only be flagged but none are
  silently corrected.
- `outputs/patient_features.csv`: one row per Lab 4 patient. A read-only
  SQLite connection and integrity/foreign-key checks protect the input.
  The workflow verifies at most one sample per patient before the
  clinical left join. Lab 4 SQL creates a complete patient × five-gene
  grid, normalizes gene symbols, and counts mutation records with a
  classification other than `Silent`. Python pivots TP53, KRAS, EGFR,
  STK11 and KEAP1 counts into columns. Patients with zero eligible
  recorded mutations remain present in the dataset.
- `outputs/combined_features.csv`: a union of both tables with `source`
  and unique `record_id` columns (`lab3:<sample_id>` or
  `lab4:<patient_id>`). The datasets have no verified crosswalk, so this
  is a source-labeled stacked table, not a fabricated patient match.
  Blank cells mean missing/not applicable and a mutation of zero means
  no eligible event is recorded.
- `outputs/report.html`: standalone report containing an SVG bar chart
  and text. `outputs/summary.txt` contains the same numerical summary.
  It reports source counts, glucose QC and the median among QC-ok
  samples, missing stages, and mutation-carrier counts in Lab 4.

Inputs are included under `data/raw/`: the Lab 3 CSV was copied from the
prior Lab 3 folder, and `cohort.db` from Lab 4. The cleaning helpers
were adapted to remove pandas/numpy; both SQL files are reused directly.

## Execution evidence

Actual combined stdout/stderr is saved in `evidence/01_clean_run.log`,
`02_partial_run.log`, `03_restored_run.log`, and `04_noop_run.log`. The
first includes both input branches and all downstream jobs. The second
includes only cleaning, combination, reporting and the aggregate `all`
target. The database query output is reused. The third restores outputs
from the original raw CSV. The fourth confirms that every target is up
to date and no jobs run.

`evidence/verification.json` records the exact edited sample/value,
before/after SHA-256 hashes and modification times. Assertions require
the query output's hash **and** modification time to stay identical,
downstream modification times to change, the combined content hash to
change, all restored output hashes to match the clean run, and the no-op
run to leave every output untouched. Final delivered outputs use the
restored original input. `evidence/environment.txt` records the tested
runtime; `requirements-lock.txt` records the installed package versions
for stricter environment recreation
(`pip install -r requirements-lock.txt`).

See `AI_USAGE.md` for AI assistance and design decisions.

## Results from the verified run

The final table has 626 records: 60 Lab 3 samples and 566 Lab 4
patients. There are 47 QC-ok glucose values (median 148.0 mg/dL) and 13
values flagged for unit/value review. Among Lab 4 patients, 54 have
missing stage. Recorded non-Silent mutation carriers are TP53 287, KRAS
168, EGFR 69, STK11 74, and KEAP1 102. These are per-gene carrier counts
and can overlap across patients.
