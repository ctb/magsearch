# Search (very) large public databases with sourmash sketches

Run it like so:

```
snakemake -s magsearch.snakefile --configfile config.yml -j 32
```

Needs ~40 GB of RAM, 32 cores.

## To run "integration" test on farm, use:

```
snakemake -s magsearch.snakefile -j 2 --configfile config-test.yml
```
