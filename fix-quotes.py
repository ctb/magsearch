#! /usr/bin/env python
import sys

with open(sys.argv[1], 'rt') as fp:
    data = fp.read()

data = data.replace("\n'", '\n"')
data = data.replace("""','""", '''","''')
data = data.replace("""',""", '''",''')

with open(sys.argv[2], 'wt') as fp:
    fp.write(data)
