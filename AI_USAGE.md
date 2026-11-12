# AI assistance for Lab 5

## Assistant(s) Used

**Model:** ChatGPT, GPT-6.1 Sol

------------------------------------------------------------------------

## Prompt and accepted/rejected decisions

| Example prompt | AI design suggestion or alternative | Disposition | Justification/evidence |
|----|----|----|----|
| "How should I organize my Snakefile so [Lab 3] CSV cleaning and [Lab 4] SQLite queries can run independently, with a combine rule and a report rule downstream?" | Use Snakemake with independent clean/query rules feeding combine/report | Accepted in implementation | Makes parallel branches and selective downstream reruns visible. Full and partial logs show the scheduler's actual jobs. |
| "My query rule reads a SQLite database, a Python script, and two SQL files. How should I declare these inputs so editing a script or query triggers the affected rules?" | Declare Python scripts and SQL files alongside data inputs | Accepted in implementation | Changes to analysis code/query definitions invalidate dependent artifacts; scripts have no hidden sibling-folder reads. |
| "My repository path contains spaces. How can I pass file paths safely from Snakemake shell commands and use the same Python interpreter that launched Snakemake?" | Quote every shell argument with Snakemake `:q` and use the current Python interpreter | Accepted in implementation | Repository paths contain spaces; the executed logs demonstrate that these commands work. |
| "The [Lab 3] table has sample IDs and the [Lab 4] table has patient IDs. How can I combine both tables for one report and retain each row's source when there is no documented crosswalk?" | Stack the unrelated datasets with explicit source labels | Accepted in implementation | There is no documented Lab 3–Lab 4 patient crosswalk. A source-labeled union preserves both datasets without inventing identity links. |
| "Could I join the [Lab 3] samples to the [Lab 4] patients by row order or by matching similar-looking IDs? What evidence would I need to justify that join?" | Join Lab 3 samples to Lab 4 patients by row order or similar-looking identifiers | Rejected design alternative | Would fabricate relationships. This was considered during design, not returned by a separate AI prompt. |
| "Would touching the raw CSV or running a dry-run demonstrate selective recomputation? How can I change one glucose value and verify which outputs reran, then restore the input?" | Prove a rerun only by touching a file or showing a dry-run | Rejected design alternative | The delivered test edits an actual glucose value, executes jobs, checks hashes/modification times, restores the original bytes and confirms a no-op. |
| "Should I add a plotting library for a bar chart of Lab 4 mutation-carrier counts by gene, or can I generate the chart directly in the standalone HTML report?" | Add plotting dependencies for the simple report | Rejected design alternative | Inline SVG gives a reproducible figure plus text using the standard library. |

## Validation

Evidence is preserved in `evidence/` and assertions check normalized
sample keys, patient grain, database integrity and foreign keys. These
checks support workflow reproducibility, but do not validate ambiguous
dates, source units, or clinical conclusions.
