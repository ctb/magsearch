"""
Author: Luiz Irber (except for the parameter fiddling :)
Source: /group/ctbrowngrp/irber/sra_search/Snakefile
snakemake -s magsearch.snakefile --profile farm --cluster-config cluster_config.yml --jobs 32 --restart-times 1
"""

configfile: "config.yml"

rule all:
  input: 
      f"{config['out_dir']}/results/{config['query_name']}.csv"


#rule catalog_all:
#  output: "/group/ctbrowngrp/irber/sra_search/catalogs/all_wort_sigs"
#  shell: "find {config[wort_sigs]} -type f -iname '*.sig' > {output}"

rule catalog_metagenomes:
  #output: "/group/ctbrowngrp/irber/sra_search/catalogs/metagenomes"
  output: "/group/ctbrowngrp/sra_search/catalogs/metagenomes"
  run:
    import csv
    from pathlib import Path

    sraids = set(Path("/group/ctbrowngrp/irber/sra_search/inputs/mash_sraids.txt").read_text().split('\n'))

    #with open("/group/ctbrowngrp/irber/sra_search/inputs/metagenomes_source-20210416.csv") as fp:
    with open("/group/ctbrowngrp/sra_search/metagenomes_source_20220128.csv") as fp:
      data = csv.DictReader(fp, delimiter=',')
      for dataset in data:
        sraids.add(dataset['Run'])

    with open(output[0], 'w') as fout:
      for sraid in sraids:
        sig_path = Path(config['wort_sigs']) / f"{sraid}.sig"
        if sig_path.exists():
          fout.write(f"{sig_path}\n")


rule build_rust_bin:
  output: "/group/ctbrowngrp/irber/sra_search/bin/sra_search",
  conda: "/group/ctbrowngrp/irber/sra_search/env/rust.yml"
  shell: "cargo install --git https://github.com/luizirber/phd.git --rev 600dee0d812189abb6521b1c7f4f7c0a29b8fdf6 sra_search --root ."

rule search:
  output: f"{config['out_dir']}/results/{config['query_name']}.csv"
  input:
    queries = config["query_sigs"],
    #catalog = "/group/ctbrowngrp/irber/sra_search/catalogs/metagenomes",
    catalog = config["catalog"],
    bin = "/group/ctbrowngrp/irber/sra_search/bin/sra_search"
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

rule download_signatures_from_wort:
  conda: "/group/ctbrowngrp/irber/sra_search/env/aws.yml"
  shell: """
    aws s3 sync s3://wort-sra/ {params.s3_dir} --request-payer=requester
  """
