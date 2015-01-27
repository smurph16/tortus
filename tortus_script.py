"""
    MoinMoin - Extension 

    @date: 2014-01-12
    MoinMoin:ThomasWaldmann """
 

import os, sys, time
from StringIO import StringIO
from default import *

flag_quiet = 0

# ScriptRequest -----------------------------------------------------------

class ScriptRequest(object):
    """this is for scripts (tortus/*) running from the commandline (CLI)"""
       #or from the xmlrpc server (triggered by a remote xmlrpc client)? ToDo
    def __init__(self, instream, outstream, errstream):
        self.instream = instream
        self.outstream = outstream
        self.errstream = errstream

    def read(self, n=None):
        if n is None:
            data = self.instream.read()
        else:
            data = self.instream.read(n)
        return data 

    def write(self, data):
        self.outstream.write(data)

    def write_err(self, data):
        self.errstream.write(data)


class ScriptRequestCLI(ScriptRequest):
    """ When a script runs directly on the shell, a CLI request
        object is used to do I/O
    """
    def __init__(self, request):
        self.request = request

    def read(self, n=None):
        return self.request.read(n)

    def write(self, data):
        return self.request.write(data)

    def write_err(self, data):
        return self.request.write(data) # XXX use correct request method - log, error, whatever.

# class ScriptRequestStrings(ScriptRequest):
#     """ When a script gets run by our xmlrpc server, we have the input as a
#         string and we also need to catch the output / error output as strings.
#     """
#     def __init__(self, instr):
#         self.instream = StringIO(instr)
#         self.outstream = StringIO()
#         self.errstream = StringIO()

#     def fetch_output(self):
#         outstr = self.outstream.get_value()
#         errstr = self.errstream.get_value()
#         self.outstream.close()
#         self.errstream.close()
#         return outstr, errstr


# Logging -----------------------------------------------------------------

def fatal(msgtext, **kw):
    """ Print error msg to stderr and exit. """
    sys.stderr.write("\n\nFATAL ERROR: " + msgtext + "\n")
    sys.exit(1)


def log(msgtext):
    """ Optionally print error msg to stderr. """
    if not flag_quiet:
        sys.stderr.write(msgtext + "\n")


# Commandline Support --------------------------------------------------------

class TortusScript:
    import argparse

    def __init__(self, cmd, usage, argv=None, def_values=None):
        #print "argv:", argv, "def_values:", repr(def_values)
        if argv is None:
            self.argv = sys.argv[1:]
        else:
            self.argv = argv
        self.def_values = def_values
        #version?
        self.parser = argparse.ArgumentParser(
            usage="%(cmd)s [command] %(usage)s" % {'cmd': os.path.basename(sys.argv[0]), 'usage': usage, })
        if def_values:
            self.parser.set_defaults(**def_values.__dict__)

    def run(self, showtime=1):
        """ Run the main function of a command. """
        global flag_quiet
        try:
            try:
                self.options, self.args = self.parser.parse_args() #(self.argv)
                flag_quiet = self.options.quiet
                # ToDo check if we need to initialize request (self.init_request())
                self.mainloop()
            except KeyboardInterrupt:
                log("*** KeyboardInterrupt")
            except SystemExit:
                raise

class MoinScript(Script):
    """ Moin main script class """

    def __init__(self, argv=None, def_values=None):
        TortusScript.__init__(self, "tortus", "[general options] command subcommand [specific options]", argv, def_values)
        # these are options potentially useful for all sub-commands:
        #self.parser.add_option(
            #"--config-dir", metavar="DIR", dest="config_dir",
            #help=("Path to the directory containing the wiki "
                  "configuration files. [default: current directory]")
        self.parser.add_argument(
            "--wiki-url", metavar="WIKIURL", dest="wiki_url",
            help="URL of a single wiki to migrate e.g. http://localhost/mywiki/ [default: CLI]"
        

        self.parser.add_argument(
            "--page", dest="page", default='',
            help="wiki page name [default: all pages]"
        )

    def init_request(self):
        """ create request """
        from MoinMoin.web.contexts import ScriptContext
        url = self.args.wiki_url or None
        if url is not None:
            self.request = ScriptContext(url, self.options.page)
        else:
            self.request = ScriptContext()

    def mainloop(self):
        # Insert config dir or the current directory to the start of the path.
        if config_dir:
            if os.path.isdir(config_dir):
                sys.path.insert(0, os.path.abspath(config_dir))
            else:
                fatal("bad path for configuration directory. This can be edited in default.py")

        args = self.args
        if len(args) < 2:
            self.parser.print_help()
            fatal("""You must specify a command module and name:

tortus ... group create ...
tortus ... group remove ...
tortus ... group modify  ...
tortus ... permissions change ...

tortus ... page add
tortus ... page fill in more here...blah 

General options:

    --wiki-url=http://wiki.example.org/
        Mandatory for some commands and specifies the url of the wiki to operate on 

Specific options:
    Most commands need additional parameters after command subcommand

    To obtain additonal help on a command use 'moin module subcommand --help'
""")

        cmd_module, cmd_name = args[:2]
        if cmd_module == '...':
            # our docs usually tell to use moin ... cmd_module cmd_name
            # if somebody enters the ... verbatim, tell him how to do it right:
            fatal("Wrong invokation. Please do not enter ... verbatim, but give --config-dir and --wiki-url options (see help for more details).")

        from MoinMoin import wikiutil
        try:
            tortus_script = open wikiutil.importBuiltinPlugin('script.%s' % cmd_module, cmd_name, 'PluginScript')
        except :
            fatal("Command plugin %r, command %r was not found." % (cmd_module, cmd_name))

        # We have to use the args list here instead of optparse, as optparse only
        # deals with things coming before command subcommand.
        if "--help" in args or "-h" in args:
            print "MoinMoin Help - %s/ %s\n" % (cmd_module, cmd_name)
            #print plugin_class.__doc__
            print "Command line reference:"
            print "======================="
            plugin_class(args[2:], self.options).parser.print_help()
        else:
            plugin_class(args[2:], self.options).run() # all starts again there