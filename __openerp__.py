# -*- coding: utf-8 -*-
##############################################################################
#
#    Bank Reconciliation, for OpenERP
#    Copyright (C) 2013 XCG Consulting (http://odoo.consulting)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': u"Bank Reconciliation",
    'version': u"1.1",
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
