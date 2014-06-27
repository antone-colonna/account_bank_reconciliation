import time
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class AccountConflictError(osv.except_osv):

    MSG_PATTERN = _(
        u"A bank reconciliation session can only reconcile lines from a "
        u"single account.\nExpected: {first_name}\nReceived: {second_name}"
    )

    def __init__(self, cr, uid, first_account, second_account, context):
        accounts = [first_account, second_account]
        try:
            fst_name, snd_name = zip(*self.pool['account.account'].name_get(
                cr, uid, accounts, context=context
            ))[1]
        except Exception:
            fst_name, snd_name = ("ID#{}".format(acc) for acc in accounts)

        super(AccountConflictError, self).__init__(_(
            u"Error!"),
            self.MSG_PATTERN.format(first_name=fst_name, second_name=snd_name)
        )


class bank_reconciliation(osv.Model):
    _name = "account.bank.reconciliation"
    _description = "Bank Reconciliation"

    def _company_id_account_store(self, cr, uid, ids, context=None):
        reconciliation_osv = self.pool['account.bank.reconciliation']
        domain = [('account_id', 'in', ids)]
        return reconciliation_osv.search(cr, uid, domain, context=context)

    def _line_ids_store(self, cr, uid, ids, context=None):
        vals = self.read(cr, uid, ids, ['reconciliation_id'], context=context)
        return [val['reconciliation_id'][0] for val in vals]

    def _total_amount_compute(self, cr, uid, ids, name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = sum(
                line.amount_currency for line in record.line_ids
            )
        return res

    _columns = {
        'name': fields.char(
            u"Name",
            size=32,
            readonly=True,
            required=True,
        ),
        'account_id': fields.many2one(
            'account.account',
            "Account",
            required=True,
            domain=[('type', '=', 'liquidity')]
        ),
        'company_id': fields.related(
            'account_id',
            'company_id',
            type='many2one',
            relation='res.company',
            string='Company',
            readonly=True,
            store={
                _name: (lambda *a: a[3], ['account_id'], 10),
                'account.account': (
                    _company_id_account_store,
                    ['company_id'],
                    10
                )
            }
        ),
        'period_id': fields.many2one(
            'account.period',
            u"Period",
            domain=[('state', '=', 'draft')],
            required=True,
        ),
        'line_ids': fields.one2many(
            'account.bank.reconciliation.line',
            'reconciliation_id',
            u"Reconciliation Lines",
            ondelete="cascade"
        ),
        'total_amount': fields.function(
            _total_amount_compute,
            string=u"Total Amount",
            type='float',
            digits_compute=dp.get_precision('Account'),
            store={
                _name: (
                    lambda self, cr, uid, ids, c: ids,
                    ['line_ids'],
                    10
                ),
                'account.bank.reconciliation.line': (
                    _line_ids_store,
                    ['amount'],
                    10
                )
            }
        ),
    }

    _defaults = {
        'name': lambda self, cr, uid, context: self.pool['ir.sequence'].get(
            cr, uid, 'account.bank.reconciliation', context=context
        )
    }

    def _check_lines(self):
        pass

    """
    def create(self, cr, uid, vals, context=None):

        account_id = vals.get('account_id')
        line_ids = vals.get('line_ids')
        if account_id and line_ids:
            self._check_lines(cr, uid, account_id, line_ids)

        return super(bank_reconciliation, self).create(
            cr, uid, vals, context=context
        )

    def write(self, cr, uid, ids, vals, context=None):

        account_id = vals.get('account_id')
        line_ids = vals.get('line_ids')

        if account_id:
            self.read(cr, uid, ids, fields, context=context)
            self._check_lines(cr, uid, account_id, line_ids)

        return super(bank_reconciliation, self).write(
            cr, uid, ids, vals, context=context
        )"""


class bank_reconciliation_line(osv.Model):
    _name = 'account.bank.reconciliation.line'
    _description = "Bank Reconciliation Line"
    _inherits = {'account.move.line': 'move_line_id'}

    def _reconciliation_store(self, cr, uid, ids, context=None):
        reconciliation_line_osv = self.pool['account.bank.reconciliation.line']
        domain = [('reconciliation_id', 'in', ids)]
        return reconciliation_line_osv.search(cr, uid, domain, context=context)

    _columns = {
        'name': fields.char(
            u"Name",
            size=32,
            readonly=True,
            required=True,
        ),
        'reconciliation_date': fields.date(
            u"Reconciliation Date",
            readonly=True,
            required=True,
        ),
        'reconciliation_id': fields.many2one(
            'account.bank.reconciliation',
            u"Reconciliation Session",
            required=True,
        ),
        'move_line_id': fields.many2one(
            'account.move.line',
            u"Journal Entry",
            domain=[
                ('move_state', '=', 'posted'),
                ('reconciliation_line_id', '=', False)
            ],
            required=True,
            ondelete='cascade',
        ),
        'company_id': fields.related(
            'reconciliation_id',
            'company_id',
            type='many2one',
            relation='res.company',
            string='Company',
            readonly=True,
            store={
                _name: (
                    lambda self, cr, uid, ids, c: ids,
                    ['reconciliation_id'],
                    10
                ),
                'account.bank.reconciliation': (
                    _reconciliation_store,
                    ['company_id'],
                    20
                )
            }
        ),
        'reconciliation_period_id': fields.related(
            'reconciliation_id',
            'period_id',
            type='many2one',
            relation='account.period',
            string=u"Reconciliation Period",
            readonly=True,
        ),
    }

    _defaults = {
        'name': lambda self, cr, uid, context: self.pool['ir.sequence'].get(
            cr, uid, 'account.bank.reconciliation.line', context=context
        ),
        'reconciliation_date': lambda *a: time.strftime('%Y-%m-%d')
    }

    _sql_constraints = [(
        'move_line_unique',
        'UNIQUE(move_line_id)',
        u"A journal entry can only be matched by one bank reconciliation line."
    )]
