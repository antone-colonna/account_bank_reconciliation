from openerp.osv import fields, osv


class bank_reconciliation_add_wizard(osv.TransientModel):

    _name = 'account.bank.reconciliation.statement'
    _description = u"Reconciliation Statement"

    def _2many_field_sum(self, cr, uid, ids, field_name, args, context=None):

        res = dict.fromkeys(ids, False)
        relation_field, value_field = args
#        related_model = self.fields_get(
#            cr, uid, allfields=[relation_field], context=context
#        )[relation_field]['relation']
#        related_osv = self.pool[related_model]

        for record in self.browse(cr, uid, ids, context=context):
            value_sum = 0
            for relation in record[relation_field]:
                value_sum += relation[value_field]
            res[record.id] = value_sum

        return res

    def _sum(self, cr, uid, ids, field_name, args, context=None):
        """Return the sum of two or more local fields."""

        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            value_sum = 0
            sign = '+'
            for arg in args:
                if arg in ('+', '-'):
                    sign = arg
                    continue
                val = record[arg]
                if sign == '-':
                    value_sum -= val
                    sign = '+'
                else:
                    value_sum += val
            res[record.id] = value_sum

        return res

    def _prepare(self, cr, uid, ids, context=None):

        line_osv = self.pool['account.move.line']
        records = self.browse(cr, uid, ids, context=context)
        reconciliation_period_str = 'reconciliation_line_id.' \
                                    'reconciliation_period_id.date_start'

        for record in records:
            end = record.period_id.date_stop
            line_domain = [
                ('move_state', '=', 'posted'),
                ('account_id', '=', record.account_id.id),
                ('period_id.date_stop', '<=', end),
            ]
            all_ids = line_osv.search(cr, uid, line_domain, context=context)

            unreconciled_domain = line_domain + [
                '|',
                ('reconciliation_line_id', '=', False),
                (reconciliation_period_str, '>', end),
            ]
            unreconciled_ids = line_osv.search(
                cr, uid, unreconciled_domain, context=context
            )

            reconciled_domain = line_domain + [
                ('reconciliation_line_id', '!=', False),
                (reconciliation_period_str, '<=', end),
            ]
            reconciled_ids = line_osv.search(
                cr, uid, reconciled_domain, context=context
            )

            vals = {
                'control_line_ids': [(6, False, all_ids)],
                'unreconciled_line_ids': [(6, False, unreconciled_ids)],
                'reconciled_line_ids': [(6, False, reconciled_ids)],
                'prepared': True
            }
            self.write(cr, uid, [record.id], vals, context=context)

    _all_line_fields = [
        'unreconciled_line_ids', 'reconciled_line_ids', 'control_line_ids'
    ]

    _columns = {
        'account_id': fields.many2one(
            'account.account',
            u"Account",
            required=True,
            domain=[('type', '=', 'liquidity')]
        ),
        'period_id': fields.many2one(
            'account.period',
            u"Period",
            domain=[('state', '=', 'draft')],
            required=True,
        ),
        'company_id': fields.related(
            'account_id',
            'company_id',
            type='many2one',
            relation='res.company',
            string='Company',
            readonly=True,
            store={_name: (lambda *a: a[3], ['account_id'], 10)}
        ),
        'prepared': fields.boolean(u"Prepared"),
        'print_unreconciled': fields.boolean(u"Print Unreconciled Lines"),
        'print_reconciled': fields.boolean(u"Print Reconciled Lines"),
        'control_line_ids': fields.many2many(
            'account.move.line',
            'bank_reconciliation_statement_control_rel',
            'wizard_id',
            'line_id',
            string=u"All Journal Entries (control)",
            readonly=True,
        ),
        'unreconciled_line_ids': fields.many2many(
            'account.move.line',
            'bank_reconciliation_statement_unreconciled_rel',
            'wizard_id',
            'line_id',
            string=u"Unreconciled Journal Entries",
            readonly=True,
        ),
        'reconciled_line_ids': fields.many2many(
            'account.move.line',
            'bank_reconciliation_statement_reconciled_rel',
            'wizard_id',
            'line_id',
            string=u"Reconciled Journal Entries",
            readonly=True,
        ),
        'unreconciled_total_debit': fields.function(
            _2many_field_sum,
            arg=('unreconciled_line_ids', 'debit_curr'),
            type='float',
            string=u"Unreconciled Debit",
            store={_name: (lambda *a: a[3], ['unreconciled_line_ids'], 10)}
        ),
        'unreconciled_total_credit': fields.function(
            _2many_field_sum,
            arg=('unreconciled_line_ids', 'credit_curr'),
            type='float',
            string=u"Unreconciled Credit",
            store={_name: (lambda *a: a[3], ['unreconciled_line_ids'], 10)}
        ),
        'unreconciled_total_balance': fields.function(
            _sum,
            arg=['unreconciled_total_debit', '-', 'unreconciled_total_credit'],
            type='float',
            string=u"Unreconciled Balance",
            store={_name: (lambda *a: a[3], ['unreconciled_line_ids'], 20)}
        ),
        'reconciled_total_debit': fields.function(
            _2many_field_sum,
            arg=('reconciled_line_ids', 'debit_curr'),
            type='float',
            string=u"Reconciled Debit",
            store={_name: (lambda *a: a[3], ['reconciled_line_ids'], 10)}
        ),
        'reconciled_total_credit': fields.function(
            _2many_field_sum,
            arg=('reconciled_line_ids', 'credit_curr'),
            type='float',
            string=u"Reconciled Credit",
            store={_name: (lambda *a: a[3], ['reconciled_line_ids'], 10)}
        ),
        'reconciled_total_balance': fields.function(
            _sum,
            arg=['reconciled_total_debit', '-', 'reconciled_total_credit'],
            type='float',
            string=u"Reconciled Balance",
            store={_name: (lambda *a: a[3], ['reconciled_line_ids'], 20)}
        ),
        'both_total_debit': fields.function(
            _sum,
            arg=['unreconciled_total_debit', 'reconciled_total_debit'],
            type='float',
            string=u"Reconstituted Debit",
            store={_name: (lambda *a: a[3], _all_line_fields, 30)}
        ),
        'both_total_credit': fields.function(
            _sum,
            arg=['unreconciled_total_credit', 'reconciled_total_credit'],
            type='float',
            string=u"Reconstituted Credit",
            store={_name: (lambda *a: a[3], _all_line_fields, 30)}
        ),
        'both_total_balance': fields.function(
            _sum,
            arg=['unreconciled_total_balance', 'reconciled_total_balance'],
            type='float',
            string=u"Reconstituted Balance",
            store={_name: (lambda *a: a[3], _all_line_fields, 30)}
        ),
        'control_total_debit': fields.function(
            _2many_field_sum,
            arg=('control_line_ids', 'debit_curr'),
            type='float',
            string=u"Control Debit",
            store={_name: (lambda *a: a[3], ['control_line_ids'], 10)}
        ),
        'control_total_credit': fields.function(
            _2many_field_sum,
            arg=('control_line_ids', 'credit_curr'),
            type='float',
            string=u"Control Credit",
            store={_name: (lambda *a: a[3], ['control_line_ids'], 10)}
        ),
        'control_total_balance': fields.function(
            _sum,
            arg=['control_total_debit', '-', 'control_total_credit'],
            type='float',
            string=u"Control Balance",
            store={_name: (lambda *a: a[3], ['control_line_ids'], 20)}
        ),
        'theoretical_balance': fields.function(
            _sum,
            arg=['control_total_balance', '-', 'unreconciled_total_balance'],
            type='float',
            string=u"Theoretical Balance",
            store={_name: (lambda *a: a[3], _all_line_fields, 30)}
        ),
    }

    _defaults = {
        'print_unreconciled': True,
        'print_reconciled': False,
    }

    def preview(self, cr, uid, ids, context=None):

        self._prepare(cr, uid, ids, context=context)

        win_obj = self.pool.get('ir.actions.act_window')
        res = win_obj.for_xml_id(
            cr, uid, 'account_bank_reconciliation',
            'action_bank_reconciliation_statement', context=context
        )
        res.update(res_id=ids[0])
        return res

    def print_report(self, cr, uid, ids, context=None):

        self._prepare(cr, uid, ids, context=context)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.bank.reconciliation.statement',
            'datas': {},
        }
