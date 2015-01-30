"""
    MoinMoin - Acts as the entry point for all tortus commands. 
    Controls general options for all commands. 


    TODO: Integrate script with individual tortus commands

    @date: 2014-01-12
    @author: Sarah Murphy
    
    MoinMoin:ThomasWaldmann """
 

import os, sys, time
from StringIO import StringIO
from default import *
from MoinMoin.script import MoinScript, Script
from MoinMoin.util import pysupport

flag_quiet = 0

class ArgumentScript(Script):
    """Initialises a generic parser to route commands to various sub-commands"""
    def __init__(self, cmd, usage, args=None, def_values=None):
        #print "argv:", argv, "def_values:", repr(def_values)

        import argparse
        #May not need this
        if args is None:
            self.args = argparse.Namespace()
        else:
            self.args = argparse.Namespace()
        self.def_values = def_values

        global _start_time
        _start_time = time.clock()

        from MoinMoin import version

        rev = "%s %s [%s]" % (version.project, version.release, version.revision)
        sys.argv[0] = cmd

        self.parser = argparse.ArgumentParser(
            usage="%(cmd)s [command] %(usage)s" % {'cmd': os.path.basename(sys.argv[0]), 'usage': usage, },
            add_help=False)
        if def_values:
            self.parser.set_defaults(**def_values.__dict__)
        self.parser.add_argument(
            "-q", "--quiet",
            action="store_true", dest="quiet",
            help="Be quiet (no informational messages)"
        )
        self.parser.add_argument(
            "--show-timing",
            action="store_true", dest="show_timing", default=False,
            help="Show timing values [default: False]"
        )

    #I haven't overridden this function....may not need it
    def run(self, showtime=1):
        """ Run the main function of a command. """
        global flag_quiet
        try:
            try:
                self.options = self.parser.parse_args()
                print self.options
                self.args = self.parser.parse_args()
                flag_quiet = self.options.quiet
                # ToDo check if we need to initialize request (self.init_request())
                self.mainloop()
            except KeyboardInterrupt:
                log("*** Interrupted by user!")
            except SystemExit:
                showtime = 0
                raise
        finally:
            if showtime:
                self.logRuntime()

class TortusScript(ArgumentScript):
    """ Tortus Scripting Class. Creates generic arguments applicable to all tortus sub-commands """

    def __init__(self, argv=None, def_values=None): 
        ArgumentScript.__init__(self, "tortus", "[general options] command subcommand [specific options]", argv, def_values)
        # these are options potentially useful for all sub-commands:
        #self.parser.add_option(
            #"--config-dir", metavar="DIR", dest="config_dir",
            #help=("Path to the directory containing the wiki configuration files. [default: current directory]")
        self.parser.add_argument("command", help="the operation to undertake on the wiki....options/choices")
        self.parser.add_argument("subcommand", help="the subcommand for the wiki operation")
        self.parser.add_argument(
            "--wiki-url", metavar="WIKIURL", dest="wiki_url",
            help="URL of a single wiki to migrate e.g. http://localhost/mywiki/ [default: CLI]"
        )
        self.parser.add_argument(
            "--page", dest="page", default='',
            help="wiki page name [default: all pages]"
        )
    # I have to update this and override it because otherwise it will break. ? How useful is it though
    # def _update_option_help(self, opt_string, help_msg):
    #     """ Update the help string of an option. """
    #     for option in self.parser.option_list:
    #         if option.get_opt_string() == opt_string:
    #             option.help = help_msg
    #             break 

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
        print args
        if not (args.command):
            self.parser.print_help()
            fatal("""You must specify a command module and name:

tortus ... create ...
tortus ... remove ...
tortus ... modify  ...
tortus ... permissions ...
tortus ... page add
tortus ... page fill in more commands here

General options:

    --wiki-url=http://wiki.example.org/
        Mandatory for some commands and specifies the url of the wiki to operate on 

Specific options:
    Most commands need additional parameters after command subcommand

    To obtain additonal help on a command use 'moin module subcommand --help'
""")
        #d = vars(args)
        cmd_module = args.command 
        print cmd_module
        cmd_name = args.subcommand
        print cmd_name
        #try:
        #from %s import %s % (cmd_module, cmd_name)
        #tortus = OperationScript()
        #tortusModule = importOperation('script.%s' % cmd_module, cmd_name, 'OperationScript')
        #except:
        tortus = importCommand(cmd_module, cmd_name)
        
        #print ("Command plugin %r, command %r was not found." % (cmd_module, cmd_name))

        # We have to use the args list here instead of optparse, as optparse only
        # deals with things coming before command subcommand.
        if "--help" in args or "-h" in args:
            print "MoinMoin Help - %s/ %s\n" % (cmd_module, cmd_name)
            #print plugin_class.__doc__
            print "Command line reference:"
            print "======================="
            #plugin_class(args[2:], self.options).parser.print_help()
        else:
            
            tortus.run() # all starts again there


#############################################################################
### Operations
#############################################################################

class OperationError(Exception):
    """ Base class for operation errors """

class OperationMissingError(OperationError):
    """ Raised when an operation is not found """

class OperationAttributeError(OperationError):
    """ Raised when an operation does not contain an attribute """

def importOperation(cfg, kind, name, function="execute"):
    """ Import tortus operation

    Returns <function> attr from a plugin module <name>.
    If <function> attr is missing, raise PluginAttributeError.
    If <function> is None, return the whole module object.

    If <name> plugin can not be imported, raise PluginMissingError.

    kind may be one of 'action', 'formatter', 'macro', 'parser' or any other
    directory that exist in MoinMoin or data/plugin.

    Wiki plugins will always override builtin plugins. If you want
    specific plugin, use either importWikiPlugin or importBuiltinPlugin
    directly.

    @param cfg: wiki config instance
    @param kind: what kind of module we want to import
    @param name: the name of the module
    @param function: the function name
    @rtype: any object
    @return: "function" of module "name" of kind "kind", or None
    """
    #try:
    print builtinOperations('create')
    return importBuiltinOperation(kind, name, function)
    #except OperationMissingError:
    print "Could not find the operation"
        #return importBuiltinOperation(kind, name, function)

def importCommand(cmd_module, cmd_name): # Needs a try/except
    modulename = "%s.%s"% (cmd_module, cmd_name)
    module = __import__(modulename)
    return module

def importOperationPlugin(cfg, kind, name, function="execute"): #extensible
    """ Import operation from the wiki data directory
    """
    operations = wikiOperations(kind, cfg)
    modname = operations.get(name, None)
    if modname is None:
        raise OperationMissingError()
    moduleName = '%s.%s' % (modname, name)
    return importNameFromOperation(moduleName, function)


def importBuiltinOperation(kind, name, function="execute"):
    """ Import operation from Tortus package"""
    if not name in builtinOperations(kind):
        raise OperationMissingError()
    moduleName = 'tortus.%s.%s' % (kind, name)
    print "helo" + moduleName
    return importNameFromOperation(moduleName, function)


def importNameFromOperation(moduleName, name):
    """ Return <name> attr from <moduleName> module,
        raise PluginAttributeError if name does not exist.

        If name is None, return the <moduleName> module object.
    """
    if name is None:
        fromlist = []
    else:
        fromlist = [name]
    module = __import__(moduleName, globals(), {}, fromlist)
    if fromlist:
        # module has the obj for module <moduleName>
        try:
            return getattr(module, name)
        except AttributeError:
            raise OperationAttributeError
    else:
        # module now has the toplevel module of <moduleName> (see __import__ docs!)
        components = moduleName.split('.')
        for comp in components[1:]:
            module = getattr(module, comp)
        return module


def builtinOperations(kind):
    """ Gets a list of modules in tortus.'kind'

    @param kind: what kind of modules we look for
    @rtype: list
    @return: module names
    """
    import importlib
    modulename = "tortus." + kind
    print modulename
    command_module = importlib.import_module(modulename)
    #from os.path.dirname(os.path.abspath)(__file__)
    return command_module


def wikiOperations(kind, cfg):
    """
    Gets a dict containing the names of all operations of @kind
    as the key and the containing module name as the value.

    @param kind: what kind of modules we look for
    @rtype: dict
    @return: plugin name to containing module name mapping
    """
    # short-cut if we've loaded the dict already
    # (or already failed to load it)
    from MoinMoin import multiconfig
    cfg = getConfig(wiki_url)

    # cache = cfg._site_plugin_lists
    # if kind in cache:
    #     result = cache[kind]
    # else:
    #     result = {}
    #     for modname in cfg._plugin_modules:
    #         try:
    #             module = pysupport.importName(modname, kind)
    #             packagepath = os.path.dirname(module.__file__)
    #             plugins = pysupport.getPluginModules(packagepath)
    #             for p in plugins:
    #                 if not p in result:
    #                     result[p] = '%s.%s' % (modname, kind)
    #         except AttributeError:
    #             pass
    #     cache[kind] = result
    # return result


def getOperations(kind, cfg):
    """ Gets a list of operation names of kind

    @param kind: what kind of modules we look for
    @rtype: list
    @return: module names
    """
    # Copy names from builtin plugins - so we dont destroy the value
    all_operations = builtinOperations(kind)[:]
    # Add extension plugins without duplicates
    for operation in wikiOperations(kind, cfg):
        if operation not in all_operations:
            all_operations.append(operation)
    return all_operations


# def searchAndImportPlugin(cfg, type, name, what=None):
#     type2classname = {"parser": "Parser",
#                       "formatter": "Formatter",
#     }
#     if what is None:
#         what = type2classname[type]
#     mt = MimeType(name)
#     plugin = None
#     for module_name in mt.module_name():
#         try:
#             plugin = importPlugin(cfg, type, module_name, what)
#             break
#         except PluginMissingError:
#             pass
#     else:
#         raise PluginMissingError("Plugin not found! (%r %r %r)" % (type, name, what))
#     return plugin
