	#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
    Tortus - "tortus" is the main script command and calls other modules as
    a sub-command.

    Usage: tortus cmdmodule cmdname [options]

    @author: 2014 Sarah Murphy
"""

def run():
    from MoinMoin.script import MoinScript
    from tortus import TortusScript
    TortusScript().run(showtime=0)

if __name__ == "__main__":
    # Insert the path to MoinMoin in the start of the path
    import sys, os
    # we use position 1 (not 0) to give a config dir inserted at 0 a chance
    # beware: we have a wikiconfig.py at the toplevel directory in the branch
    sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), os.pardir, os.pardir)))

    run()

