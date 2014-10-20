# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################
{
    'name': u"Bank Reconciliation",
    'version': u"1.0.2",
    'author': u"XCG Consulting",
    'category': u"Custom Module",
    'description': u"""Bank Reconciliation.
    """,
    'website': u"",
    'depends': [
        'base',
        'account',
        'account_streamline',
        'report_webkit',
        'web_m2o_enhanced',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'wizard/bank_reconciliation_add_view.xml',
        'wizard/bank_reconciliation_statement_view.xml',
        'views/bank_reconciliation_view.xml',
        'views/menu.xml',
        'data/reconciliation_sequence.xml',
        'data/reconciliation_line_sequence.xml',
        'bank_reconciliation_webkit_view.xml',
    ],
    'demo': [
    ],
    'css': [
    ],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
