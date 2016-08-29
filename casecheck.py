#!/usr/bin/env python2

import os

for root, dirs, files in os.walk("."):
	content = dirs + files
	for one in content:
		for other in content:
			if one != other:
				if one.lower() == other.lower():
					print(root + "/" + one)
