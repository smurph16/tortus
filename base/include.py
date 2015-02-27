# -*- coding: utf-8 -*-
"""
    MoinMoin - macro to overlay data on a template

    <<IncludeWithVals(template, vardict)>>

    @copyright: 2012 Gordon Messmer <gordon@dragonsdawn.net>
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.macro import Macro

_sysmsg = u'<p><strong class="%s">%s</strong></p>'

def macro_IncludeWithVals(macro, template=u"", vardict=None):
    request = macro.request
    _ = request.getText

    # parse and check arguments
    if not template:
        return (_sysmsg % ('error', _('Invalid include arguments "%s"!')) % (template, ))
    if not hasattr(request, 'ReqVars'):
        request.ReqVars = {}

    this_page = macro.formatter.page.page_name
    if vardict:
        request.ReqVars['vardict'] = vardict
    else:
        request.ReqVars['vardict'] = this_page + 'Dict'

    if request.args.has_key('edit'):
        formtag = u'<form action="%s/%s?action=savedict" method="post">\n<input type="hidden" name="vardict" value="%s" />' % \
            (request.script_root, this_page, request.ReqVars['vardict'])
        formend = u'<input type="submit" value="%s" />\n</form>\n' % \
            _('Save form values')
        return formtag + Macro(macro.parser).execute('Include', template) + formend
    else:
        return Macro(macro.parser).execute('Include', template)
