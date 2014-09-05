from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.addons.account_bank_reconciliation.model.bank_reconciliation \
        import AccountConflictError


class bank_reconciliation_add_wizard(osv.TransientModel):

    _name = 'account.bank.reconciliation.add'
    _description = "Add Lines to Reconcile"
    _inherits = {'account.bank.reconciliation': 'reconciliation_id'}

    _columns = {
        'reconciliation_id': fields.many2one(
            'account.bank.reconciliation',
            'Session',
            ondelete='cascade',
            required=True,
        ),
        'move_line_ids': fields.many2many(
            'account.move.line',
            'bank_reconciliation_add_wizard_line_rel',
            'wizard_id',
            'line_id',
            string=u"Journal Entries",
            required=True,
        ),
        'account_displayed': fields.many2one(
            'account.account',
            "Account",
        )
    }

    def default_get(self, cr, uid, fields_list, context=None):

        if not context:
            context = {}

        defaults = super(bank_reconciliation_add_wizard, self).default_get(
            cr, uid, fields_list, context=context
        )
        reconciliation_id = defaults.get('reconciliation_id', False)
        account_id = defaults.get('account_id', False)

        if reconciliation_id:
            rec_osv = self.pool['account.bank.reconciliation']
            columns = ['account_id', 'period_id']
            reconciliation = rec_osv.read(
                cr, uid, reconciliation_id, columns, context=context
            )
            defaults['period_id'] = reconciliation['period_id'][0]
            reconciliation_account_id = reconciliation['account_id'][0]
            if account_id:
                if reconciliation_account_id != account_id:
                    raise AccountConflictError(
                        cr, uid, reconciliation_account_id, account_id, context
                    )
            else:
                account_id = defaults['account_id'] = reconciliation_account_id

        else:
            line_ids = context['active_ids']
            line_osv = self.pool['account.move.line']
            r_fields = ['account_id', 'move_state', 'reconciliation_line_id']
            lines = line_osv.read(cr, uid, line_ids, r_fields, context=context)
            if not account_id:
                account_id = defaults['account_id'] = lines[0]['account_id'][0]
                account_osv = self.pool['account.account']
                account_type = account_osv.read(
                    cr, uid, account_id, ['type'], context=context
                )['type']
                if account_type != 'liquidity':
                    raise osv.except_osv(
                        _(u"Error!"),
                        _(u"Can only work on a liquidity account.")
                    )
            for line in lines:
                if line['move_state'] != 'posted':
                    raise osv.except_osv(
                        _(u"Error!"),
                        _(u"Can only select posted lines.")
                    )
                if line['reconciliation_line_id'] is not False:
                    raise osv.except_osv(
                        _(u"Error!"),
                        _(u"Cannot select lines that have been reconciled.")
                    )
                line_account_id = line['account_id'][0]
                if line_account_id != account_id:
                    raise AccountConflictError(
                        cr, uid, account_id, line_account_id, context
                    )
            defaults['move_line_ids'] = line_ids

        defaults['account_displayed'] = account_id

        return defaults

    def add(self, cr, uid, ids, context=None):

        records = self.browse(cr, uid, ids, context=context)

        for record in records:
            reconciliation = record.reconciliation_id.id
            line_vals = {'reconciliation_id': reconciliation}
            lines = [
                (0, 0, dict(line_vals, move_line_id=move_line.id))
                for move_line in record.move_line_ids
            ]
            rec_osv = self.pool['account.bank.reconciliation']
            rec_osv.write(
                cr, uid, reconciliation, {'line_ids': lines}, context=context
            )

        win_obj = self.pool.get('ir.actions.act_window')
        res = win_obj.for_xml_id(
            cr, uid, 'account_bank_reconciliation',
            'action_bank_reconciliation_new', context=context
        )
        res.update(res_id=reconciliation)
        return res
