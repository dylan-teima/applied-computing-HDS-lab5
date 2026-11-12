import sys

PYTHON = sys.executable

rule all:
    input:
        'outputs/combined_features.csv',
        'outputs/summary.txt',
        'outputs/report.html'

rule clean_samples:
    input:
        raw='data/raw/lab3-messy-data/messy_samples.csv',
        code='scripts/clean_samples.py'
    output: 'outputs/cleaned_samples.csv'
    shell: '{PYTHON:q} {input.code:q} {input.raw:q} {output:q}'

rule query_patients:
    input:
        db='data/raw/lab4-cbioportal-luad/cohort.db',
        clinical='sql/patient_clinical.sql',
        genes='sql/patient_gene_counts.sql',
        code='scripts/query_patients.py'
    output: 'outputs/patient_features.csv'
    shell: '{PYTHON:q} {input.code:q} {input.db:q} {input.clinical:q} {input.genes:q} {output:q}'

rule combine:
    input:
        samples='outputs/cleaned_samples.csv',
        patients='outputs/patient_features.csv',
        code='scripts/combine.py'
    output: 'outputs/combined_features.csv'
    shell: '{PYTHON:q} {input.code:q} {input.samples:q} {input.patients:q} {output:q}'

rule report:
    input:
        table='outputs/combined_features.csv',
        code='scripts/report.py'
    output:
        text='outputs/summary.txt',
        html='outputs/report.html'
    shell: '{PYTHON:q} {input.code:q} {input.table:q} {output.text:q} {output.html:q}'
