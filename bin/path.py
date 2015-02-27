import os, sys
thisdir = os.path.dirname(__file__)
libdir = os.path.join(os.path.dirname(thisdir), 'base')
tordir = os.path.dirname(libdir)

if libdir not in sys.path:
	sys.path.insert(0, libdir)
if tordir not in sys.path:
	sys.path.insert(0, tordir)
