import subprocess
import csv
from pathlib import Path
import pandas as pd

testdata_path = Path('tests/test-data')


def run_summarize(magsearch_csv, runinfo_csv, *args, fail_ok=False):
    args = [ str(x) for x in args ]

    args = ['./summarize-results.py', '--run', runinfo_csv, magsearch_csv] + args
    p = subprocess.run(args, capture_output=True)
    if p.returncode != 0 and not fail_ok:
        raise Exception(p)

    return p


def test_1_runme():
    # test a basic run!
    p = run_summarize(testdata_path / 'gut.magsearch.csv',
                      testdata_path / 'gut.runinfo.csv',
                      '-t', '0.01')

    out = p.stdout.decode('utf-8')
    err = p.stderr.decode('utf-8')

    print(out)
    print(err)

    assert 'Homo sapiens            1' in out
    assert 'human gut metagenome    1' in out
    assert 'mouse gut metagenome    1' in out

    assert 'Of 3 MAGsearch results, 3 have non-null metadata' in err
    assert '3 distinct metagenomes found.' in err


def test_2_annot_out(tmp_path):
    # test a basic run!
    p = run_summarize(testdata_path / 'gut.magsearch.csv',
                      testdata_path / 'gut.runinfo.csv',
                      '-t', '0.01', '-o', tmp_path / 'annot.csv')

    out = p.stdout.decode('utf-8')
    err = p.stderr.decode('utf-8')

    print(out)
    print(err)

    df = pd.read_csv(tmp_path / 'annot.csv')

    assert len(df) == 3
    assert len(df.ScientificName) == 3
    assert set(df.ScientificName) == set(['human gut metagenome',
                                          'mouse gut metagenome',
                                          'Homo sapiens'])
                                         
    assert set(df.Run) == set(['ERR3321951', 'ERR346577', 'SRR5936022'])
