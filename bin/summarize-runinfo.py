#! /usr/bin/env python
"""
Summarize magsearch results.
"""
import sys
import pandas as pd
import argparse
import os


def main():
    p = argparse.ArgumentParser()
    p.add_argument('run_info_sra')
    p.add_argument('-N', '--display-num-rows', type=int, default=20)
    p.add_argument('-M', '--markdown', action='store_true')
    args = p.parse_args()

    print(f"loading runinfo from '{args.run_info_sra}'", file=sys.stderr)
    run_info = pd.read_csv(args.run_info_sra)
    print(f"...done. Loaded {len(run_info)} rows.", file=sys.stderr)
    print("", file=sys.stderr)

    print("\nBreakdown of ScientificName:\n", file=sys.stderr)
    summary = run_info["ScientificName"].value_counts()[:args.display_num_rows]    
    if args.markdown:
        print(summary.to_markdown())
    else:
        print(summary)


if __name__ == '__main__':
    sys.exit(main())
