#!/usr/bin/env python2

import os

def is_casedupe(name, names):
	for n in names:
		if n != name:
			if n.lower() == name.lower():
				return True
	return False

for root, dirs, files in os.walk("."):
	content = dirs + files
	for entry in content:
		if is_casedupe(entry, content):
			print(root + "/" + entry)
