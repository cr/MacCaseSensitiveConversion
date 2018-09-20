#!/usr/bin/env python2

import os

for root, dirs, files in os.walk("."):
	content = dirs + files
	all_filenames = set()
	for filename in content:
		if filename.lower() in all_filenames:
			print(root + "/" + filename)
		all_filenames.add(filename.lower())
