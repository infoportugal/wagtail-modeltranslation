#!/usr/bin/env python
import sys

version = sys.argv[1]
if version.startswith('http'):
    print(version)
else:
    # Bump the last component as a number: 7.19 -> 7.20, not 7.110
    parts = version.split('.')
    next_version = '.'.join(parts[:-1] + [str(int(parts[-1]) + 1)])
    print('Wagtail>=%s,<%s' % (version, next_version))
