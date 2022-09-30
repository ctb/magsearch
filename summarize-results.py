#! /usr/bin/env python
import sys
import pandas as pd
import argparse
import os


def strip_quotes(x):
    return x.strip("'")

def extract_run_acc(x):
    # get just the end filename
    x = x.strip("'")
    x = os.path.basename(x)
    # remove extension '.sig'
    y, ext = os.path.splitext(x)
    assert ext == '.sig', ext
    return y

# this can be used in case we have .gz, .fasta, .fa, etc in the query filename
def remove_extension(x):
    x = os.path.basename(x)
    y, ext = os.path.splitext(x)
    while ext in ('.gz', '.fasta', '.fa', '.fna'):
        x = y
        y, ext = os.path.splitext(x)
    return y


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-info-sra', required=True)
    p.add_argument('magsearch_csv')
    p.add_argument('-t', '--containment-threshold', type=float, default=0.20)
    p.add_argument('-N', '--display-num-rows', type=int, default=20)
    p.add_argument('-o', '--output-annotated-csv')
    args = p.parse_args()

    print(f"loading runinfo from '{args.run_info_sra}'", file=sys.stderr)
    run_info = pd.read_csv(args.run_info_sra)
    print(f"...done. Loaded {len(run_info)} rows.", file=sys.stderr)
    print("", file=sys.stderr)

    print(f"loading magsearch results from '{args.magsearch_csv}'",
          file=sys.stderr)
    magsearch_df = pd.read_csv(args.magsearch_csv)
    print(f"...done. Loaded {len(magsearch_df)} rows.", file=sys.stderr)
    print("", file=sys.stderr)

    print(f"filtering magsearch results at a threshold of {args.containment_threshold:.02f}", file=sys.stderr)
    magsearch_df = magsearch_df[magsearch_df.containment >= args.containment_threshold]
    print(f"...{len(magsearch_df)} left.", file=sys.stderr)
    print("", file=sys.stderr)
    
    # clean up the MAGsearch columns
    print(f"cleaning up magsearch result columns...", file=sys.stderr)
    magsearch_df['Run'] = magsearch_df['Run'].apply(extract_run_acc)
    magsearch_df['query'] = magsearch_df['query'].apply(strip_quotes)

    # join in the ScientificName column from run_info.
    print(f"joining magsearch results with run info...", file=sys.stderr)
    magsearch2_df = magsearch_df.set_index('Run').join(run_info.set_index('Run')['ScientificName'])

    null_df = magsearch2_df[magsearch2_df['ScientificName'].isnull()]
    print(f"ignoring {len(null_df)} magsearch rows b/c null ScientificName.",
          file=sys.stderr)
    print("", file=sys.stderr)

    magsearch3_df = magsearch2_df[~magsearch2_df['ScientificName'].isnull()]
    print(f"Of {len(magsearch2_df)} MAGsearch results, {len(magsearch3_df)} have non-null metadata", file=sys.stderr)

    if args.output_annotated_csv:
        print(f"writing annotated MAGsearch results to '{args.output_annotated_csv}'", file=sys.stderr)
        magsearch3_df.to_csv(args.output_annotated_csv)
        print(f"...wrote {len(magsearch3_df)} results.", file=sys.stderr)
        print("", file=sys.stderr)

    # distinct metagenome IDs
    sra_acc_set = set(magsearch3_df.index)
    
    print(f"{len(sra_acc_set)} distinct metagenomes found.", file=sys.stderr)
    distinct_metagenomes = run_info[run_info["Run"].isin(sra_acc_set)]

    print("\nBreakdown of ScientificName across distinct metagenomes:\n", file=sys.stderr)
    print(distinct_metagenomes["ScientificName"].value_counts()[:args.display_num_rows])


if __name__ == '__main__':
    sys.exit(main())
