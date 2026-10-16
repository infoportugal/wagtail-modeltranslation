#!/usr/bin/env python
import sys

version = sys.argv[1]
if version.startswith('http'):
    print(version)
else:
    # Bump the last component as a number: 0.19 -> 0.20, not 0.110
    parts = version.split('.')
    next_version = '.'.join(parts[:-1] + [str(int(parts[-1]) + 1)])
    print('django-modeltranslation>=%s,<%s' % (version, next_version))
