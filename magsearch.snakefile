"""
Authors: Luiz Irber, N. Tessa Pierce, C. Titus Brown

Run it like so:

snakemake -s magsearch.snakefile --configfile config.yml -j 32

Needs ~40 GB of RAM for search.
"""

configfile: "config.yml"

rule all:
    input:
        f"{config['out_dir']}/results/{config['query_name']}.annot.csv"

rule build_rust_bin:
    output: "bin/searcher"
    conda: "/group/ctbrowngrp/irber/sra_search/env/rust.yml"
    shell: """
        cargo install --git https://github.com/sourmash-bio/sra_search \
             searcher --root .
    """

rule search:
    output:
        f"{config['out_dir']}/results/{config['query_name']}.csv"
    input:
        queries = config["query_sigs"],
        #catalog = "/group/ctbrowngrp/irber/sra_search/catalogs/metagenomes",
        catalog = config["catalog"],
        #bin = "/group/ctbrowngrp/irber/sra_search/bin/sra_search"
        bin = "bin/searcher",
    params:
        threshold = config.get("threshold", 0.01),
        ksize = config.get("ksize", 31),
        scaled = config.get("scaled", 1000)
    log: f"{config['out_dir']}/logs/sra_search.k{config['ksize']}.log"
    benchmark: f"{config['out_dir']}/logs/sra_search.k{config['ksize']}.benchmark"
    threads: 36
    resources:
        mem_mb=lambda wildcards, attempt: attempt * 60000,
        #runtime= 720, # 12 hours
    shell: """
        export RAYON_NUM_THREADS={threads}
        set +e
        {input.bin} --threshold {params.threshold} -k {params.ksize} \
             --scaled {params.scaled} \
             -o {output} {input.queries} {input.catalog} 2> {log}
        exit 0
    """

rule summarize:
    input:
        results = f"{config['out_dir']}/results/{config['query_name']}.csv",
        runinfo = config['runinfo'],
    output:
        annot = f"{config['out_dir']}/results/{config['query_name']}.annot.csv",
        out = f"{config['out_dir']}/results/{config['query_name']}.summary.out",
    params:
        threshold = float(config['summary_threshold'])
    shell: """
       bin/summarize-results.py --run {input.runinfo} {results} \
            -t {params.threshold} -o {output.annot} >& {output.out}
    """
