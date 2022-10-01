import subprocess
import csv


def run_search(*args, fail_ok=False):
    args = [ str(x) for x in args ]
    args.insert(0, 'bin/searcher')

    p = subprocess.run(args, capture_output=True)
    if p.returncode != 0 and not fail_ok:
        raise Exception(p)

    return p


def load_csv(filename):
    with open(filename, newline='') as fp:
        r = csv.DictReader(fp, quotechar="'")
        rows = list(r)

    return rows


def test_1():
    p = run_search(fail_ok=True)

    print(p.stdout)
    print(p.stderr)
    err = p.stderr.decode('utf-8')

    assert "The following required arguments were not provided" in err


def test_2(tmp_path):
    # search a single sketch
    query = 'tests/test-data/63-only.list.txt'
    against = 'tests/test-data/all.list.txt'
    results = tmp_path / 'xxx.txt'

    p = run_search(query, against, '-o', results)
    print(p.stdout)
    print(p.stderr)
    err = p.stderr.decode('utf-8')

    assert 'Loaded 1 query signatures' in err
    assert 'Loaded 3 sig paths in siglist' in err

    rows = load_csv(results)
    print(rows)

    assert len(rows) == 1
    row = rows[0]
    assert row['query'] == 'NC_011663.1 Shewanella baltica OS223, complete genome'
    assert row['Run'] == 'tests/test-data/63.fa.sig'
    assert row['containment'] == '1'


def test_3(tmp_path):
    # search multiple sketches
    query = 'tests/test-data/63-only.list.txt'
    against = 'tests/test-data/all.list.txt'
    results = tmp_path / 'xxx.txt'

    p = run_search(query, against, '-o', results, '--threshold', '0.1')
    print(p.stdout)
    print(p.stderr)
    err = p.stderr.decode('utf-8')

    assert 'Loaded 1 query signatures' in err
    assert 'Loaded 3 sig paths in siglist' in err

    rows = load_csv(results)
    rows.sort(key = lambda x: x['Run'])
    print(rows)

    assert len(rows) == 2
    row = rows[1]
    assert row['query'] == 'NC_011663.1 Shewanella baltica OS223, complete genome'
    assert row['Run'] == 'tests/test-data/63.fa.sig'
    assert row['containment'] == '1'

    row = rows[0]
    assert row['query'] == 'NC_011663.1 Shewanella baltica OS223, complete genome'
    assert row['Run'] == 'tests/test-data/47.fa.sig'
    assert row['containment'] == '0.48281786941580757'


def test_3_specify_ksize_scaled(tmp_path):
    # search a single sketch, but specify ksize and scaled
    query = 'tests/test-data/63-only.list.txt'
    against = 'tests/test-data/all.list.txt'
    results = tmp_path / 'xxx.txt'

    p = run_search(query, against, '-o', results, '-k', '31', '--scaled',
                   '1000')
    print(p.stdout)
    print(p.stderr)
    err = p.stderr.decode('utf-8')

    assert 'Loaded 1 query signatures' in err
    assert 'Loaded 3 sig paths in siglist' in err

    rows = load_csv(results)
    print(rows)

    assert len(rows) == 1
    row = rows[0]
    assert row['query'] == 'NC_011663.1 Shewanella baltica OS223, complete genome'
    assert row['Run'] == 'tests/test-data/63.fa.sig'
    assert row['containment'] == '1'
